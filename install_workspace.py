from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
vp = base / "apps/teacher_studio/views.py"
src = vp.read_text(encoding="utf-8")
EXTRA = r'''
    @action(detail=False, methods=["get"], url_path="recent")
    def recent(self, request):
        rows = []
        for a in self.get_queryset().order_by("-created_at")[:20]:
            try:
                lesson = json.loads(a.content)
            except Exception:
                lesson = {}
            rows.append({
                "id": str(a.id), "artifact_type": a.artifact_type, "topic": a.topic,
                "title": lesson.get("title") or a.topic, "grade_level": lesson.get("grade_level", ""),
                "curriculum": lesson.get("curriculum", ""), "language": lesson.get("language", "en"),
                "created_at": a.created_at.strftime("%d %b, %H:%M") if a.created_at else "",
                "content": a.content,
            })
        return Response(rows)
    @action(detail=False, methods=["post"], url_path="notes")
    def notes(self, request):
        data = request.data if isinstance(request.data, dict) else {}
        m = Membership.objects.filter(user=request.user, is_active=True).first()
        if not m:
            return Response({"detail": "You must belong to an institution."}, status=400)
        art = TeachingArtifact.objects.filter(id=data.get("artifact_id"), institution=m.institution).first()
        if not art:
            return Response({"detail": "Artifact not found."}, status=404)
        try:
            lesson = json.loads(art.content)
        except Exception:
            return Response({"detail": "Artifact content is not editable."}, status=400)
        lesson["teacher_notes"] = str(data.get("notes") or "")
        art.content = json.dumps(lesson, indent=2)
        art.save(update_fields=["content"])
        try:
            from apps.audit.models import AuditEvent
            AuditEvent.objects.create(institution=m.institution, actor=request.user, action="TEACHER_NOTES_EDITED",
                                      resource_type="TeachingArtifact", resource_id=str(art.id), metadata={})
        except Exception:
            pass
        return Response({"saved": True})
'''
if 'url_path="recent"' not in src:
    src = src + EXTRA
    vp.write_text(src, encoding="utf-8")
tp = base / "templates/teacher_studio/studio.html"
html = tp.read_text(encoding="utf-8")
LAYER = r'''
<style>
  .rc-item{display:block;width:100%;text-align:left;border:1px solid var(--line);border-radius:.6rem;padding:.55rem .7rem;margin-top:.45rem;background:#fff;cursor:pointer;transition:.15s;font-size:.8rem;}
  .rc-item:hover{background:var(--soft);border-color:var(--indigo);}
  .rc-item b{display:block;color:var(--indigo);font-size:.82rem;}
  .rc-item span{color:var(--mut);font-size:.7rem;}
  .notes-edit{outline:none;border:1px dashed transparent;border-radius:.4rem;padding:.2rem .3rem;min-height:1.2em;}
  .notes-edit:focus{border-color:var(--indigo);background:#fff;}
  .notes-save{font-size:.7rem;font-weight:700;color:#fff;background:var(--green2);border:none;border-radius:.45rem;padding:.3rem .6rem;cursor:pointer;margin-left:.5rem;}
  details.res-panel{border:1px solid var(--line);border-radius:.6rem;padding:.6rem .8rem;background:var(--soft);}
  details.res-panel summary{cursor:pointer;font-weight:700;color:var(--indigo);font-size:.9rem;}
</style>
<script>
(function(){
  function readBody(){return {artifact_type:document.getElementById("atype").value,topic:document.getElementById("topic").value,subtopic:document.getElementById("subtopic").value,grade_level:document.getElementById("grade").value,curriculum:document.getElementById("curr").value,week:document.getElementById("week").value,term:document.getElementById("term").value,duration:document.getElementById("duration").value,language:document.getElementById("language").value,count:document.getElementById("count").value,difficulty:document.getElementById("difficulty").value,mix:document.getElementById("mix").value};}
  function langOf(d){return (window.I18N&&window.I18N[d&&d.language==="sw"?"sw":"en"])||window.I18N.en;}
  function enhance(d){
    var doc=document.getElementById("doc");
    var old=document.getElementById("enh");if(old)old.remove();
    var html="";
    if(d.bloom&&d.bloom.length)html+='<div class="enh-box enh-ind" style="border-radius:.7rem;padding:.9rem 1rem;margin-top:1rem;font-size:.88rem;background:#EEF2FF;border-left:4px solid var(--indigo)"><b style="color:var(--indigo)">Bloom levels:</b> '+d.bloom.map(function(x){return '<span class="wb">'+esc(x)+'</span>';}).join("")+'</div>';
    if(d.word_bank&&d.kind==="quiz")html+='<div style="border-radius:.7rem;padding:.9rem 1rem;margin-top:1rem;font-size:.88rem;background:#EEF2FF;border-left:4px solid var(--indigo)"><b style="color:var(--indigo)">Word bank:</b> '+d.word_bank.map(function(x){return '<span class="wb">'+esc(x)+'</span>';}).join("")+'</div>';
    if(d.misconceptions&&d.misconceptions.length)html+='<div style="border-radius:.7rem;padding:.9rem 1rem;margin-top:1rem;font-size:.88rem;background:#FEF2F2;border-left:4px solid var(--red)"><b style="color:var(--red)">Common misconceptions:</b><ul style="margin:.4rem 0 0 1.1rem">'+d.misconceptions.map(function(x){return '<li>'+esc(x)+'</li>';}).join("")+'</ul></div>';
    if(d.homework)html+='<div style="border-radius:.7rem;padding:.9rem 1rem;margin-top:1rem;font-size:.88rem;background:#EEF2FF;border-left:4px solid var(--indigo)"><b style="color:var(--indigo)">Homework / extension:</b> '+esc(d.homework)+'</div>';
    if(html){var e=document.createElement("div");e.id="enh";e.innerHTML=html;doc.appendChild(e);}
    (d.questions||[]).forEach(function(q){
      var card=document.getElementById("qc"+q.no);if(!card||!q.hint||card.querySelector(".hintbox"))return;
      var stem=card.querySelector("p.font-medium");if(stem)stem.insertAdjacentHTML("afterend",'<div class="hintbox" style="margin-top:.5rem;background:#EEF6FF;border:1px dashed #2563EB;border-radius:.5rem;padding:.45rem .65rem;font-size:.8rem;color:#1E40AF">'+esc(q.hint)+'</div>');
    });
  }
  function wireNotes(d){
    if(!d||d.kind!=="lesson_plan")return;
    var boxes=document.querySelectorAll('#doc div[style*="FFFBEB"]');
    boxes.forEach(function(box){
      var p=box.querySelector("p:last-child");if(!p)return;
      p.classList.add("notes-edit");p.contentEditable="true";p.dataset.notes="1";
      if(!box.querySelector(".notes-save")){
        var h=box.querySelector("h3");if(!h)return;
        var b=document.createElement("button");b.className="notes-save";b.textContent="Save notes";
        b.onclick=function(){
          var token=document.querySelector("[name=csrfmiddlewaretoken]").value;
          fetch("/api/teacher/artifacts/notes/",{method:"POST",credentials:"same-origin",headers:{"X-CSRFToken":token,"Content-Type":"application/json"},body:JSON.stringify({artifact_id:window.currentArtifactId,notes:p.innerText})})
          .then(function(r){return r.json();}).then(function(j){ if(j.saved){b.textContent="Saved ✓";setTimeout(function(){b.textContent="Save notes";},1500);} });
        };
        h.appendChild(b);
      }
    });
  }
  function collapseResources(d){
    var L=langOf(d);
    var heads=document.querySelectorAll("#doc h3");
    heads.forEach(function(h){
      if(h.textContent.trim()!==L.res)return;
      var p=h.nextElementSibling;if(!p||p.tagName!=="P")return;
      if(h.parentElement.tagName==="DETAILS")return;
      var det=document.createElement("details");det.className="res-panel";
      var sum=document.createElement("summary");sum.textContent=L.res;
      h.parentNode.insertBefore(det,h);det.appendChild(sum);det.appendChild(p);h.remove();
      det.open=false;
    });
  }
  function openDoc(row){
    var d;try{d=JSON.parse(row.content);}catch(e){return;}
    window.currentContent=row.content;window.currentLesson=d;window.currentArtifactId=row.id;window.lastMark=null;
    document.getElementById("empty").classList.add("hidden");
    document.getElementById("out").classList.remove("hidden");
    var doc=document.getElementById("doc");doc.classList.remove("show-answers");
    doc.innerHTML=renderAny(d,readBody());
    var sc=document.getElementById("scorecard");if(sc)sc.remove();
    var rp=document.getElementById("reportPanel");if(rp)rp.innerHTML="";
    document.getElementById("markBtn").classList.toggle("hidden",!(d&&d.kind==="quiz"));
    enhance(d);wireNotes(d);collapseResources(d);
    if(window.lucide)lucide.createIcons();
  }
  function loadRecent(){
    fetch("/api/teacher/artifacts/recent/",{credentials:"same-origin"}).then(function(r){return r.json();}).then(function(rows){
      var list=document.getElementById("recentList");if(!list)return;
      if(!rows||!rows.length){list.innerHTML='<p style="color:var(--mut);font-size:.75rem">No materials yet.</p>';return;}
      list.innerHTML=rows.map(function(x,i){
        return '<button class="rc-item" data-i="'+i+'"><b>'+esc(x.title)+'</b><span>'+esc(x.artifact_type.replace("_"," "))+' · '+esc(x.grade_level||"—")+' · '+esc(x.created_at)+'</span></button>';
      }).join("");
      Array.prototype.forEach.call(list.querySelectorAll(".rc-item"),function(btn){
        btn.onclick=function(){openDoc(rows[parseInt(btn.dataset.i,10)]);};
      });
    }).catch(function(){});
  }
  function panel(){
    if(document.getElementById("recentCard"))return;
    var formCard=document.getElementById("genform").closest(".jf-card");
    var card=document.createElement("div");card.id="recentCard";card.className="jf-card p-5 no-print";card.style.marginTop="1.2rem";
    card.innerHTML='<h3 style="font-family:Manrope;font-weight:800;color:var(--indigo);font-size:.95rem;display:flex;align-items:center;gap:.4rem"><i data-lucide="history"></i> Recent materials</h3><div id="recentList"></div>';
    formCard.parentNode.insertBefore(card,formCard.nextSibling);
    if(window.lucide)lucide.createIcons();
    loadRecent();
    var t=null;
    new MutationObserver(function(){clearTimeout(t);t=setTimeout(loadRecent,900);}).observe(document.getElementById("doc"),{childList:true,subtree:true});
  }
  function hook(){panel();}
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",hook);else hook();
  document.getElementById("genform").addEventListener("submit",function(){setTimeout(function(){var d=window.currentLesson;enhance(d);wireNotes(d);collapseResources(d);},500);});
})();
</script>
'''
if "recentCard" not in html:
    i = html.rfind("{% endblock %}")
    html = html[:i] + LAYER + "\n" + html[i:]
    tp.write_text(html, encoding="utf-8")
print("STUDIO WORKSPACE: RECENT MATERIALS + EDITABLE NOTES + COLLAPSIBLE RESOURCES")
