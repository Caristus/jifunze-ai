from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
vp = base / "apps/teacher_studio/views.py"
src = vp.read_text(encoding="utf-8")
HELPERS = r'''
def _renumber_recompute(d):
    qs = d.get("questions") or []
    for i, q in enumerate(qs, 1):
        q["no"] = i
    d["total_marks"] = sum(q.get("marks") or 0 for q in qs)
    d["auto_markable"] = sum(q.get("marks") or 0 for q in qs if q.get("auto"))
    d["review_marks"] = sum(q.get("marks") or 0 for q in qs if not q.get("auto"))
    return d
def _apply_improve(d):
    lang = d.get("language", "en")
    low = (d.get("topic") or "the topic").lower()
    if not d.get("misconceptions"):
        d["misconceptions"] = (["Wanafunzi huchanganya " + low + " na dhana za kila siku.",
                                "Hutumia kanuni hata pale isipotumika.",
                                "Hukosa vitengo au lebo katika majibu."] if lang == "sw" else
                               ["Learners confuse " + low + " with everyday intuitions.",
                                "The rule is over-generalised to cases where it does not hold.",
                                "Units or labels are omitted in responses."])
    if not d.get("bloom"):
        d["bloom"] = (["Kumbuka", "Elewa", "Tumia", "Chambua"] if lang == "sw" else
                      ["Remember", "Understand", "Apply", "Analyse"])
    for q in (d.get("questions") or []):
        if not q.get("explain"):
            q["explain"] = ("Award credit per marking point; accept equivalent correct phrasing." if lang == "en"
                            else "Toa alama kwa kila kipengele; kubali majibu sawia sahihi.")
    d["improved"] = True
    return d
def _apply_expand(d):
    lang = d.get("language", "en")
    low = (d.get("topic") or "the topic").lower()
    kw = (_facts(low) or {}).get("kw") or [low]
    kind = d.get("kind")
    if kind == "quiz":
        specs = [("structured", 4), ("essay", 6), ("short", 2), ("match", 4)]
        extra = []
        for ty, mk in specs:
            if ty == "match":
                pairs = (_facts(low) or {}).get("pairs")
                if not pairs:
                    continue
                extra.append({"type": "match", "stem": ("Match each term to its meaning." if lang == "en" else "Oanisha kila istilahi na maana yake."),
                              "pairs": [{"term": p[0], "meaning": p[1]} for p in pairs], "meanings": [p[1] for p in pairs],
                              "marks": len(pairs), "answer": "; ".join(p[0] + " = " + p[1] for p in pairs),
                              "explain": "", "points": [], "auto": True})
                continue
            extra.append({"type": ty,
                          "stem": (("Discuss " if lang == "en" else "Jadili ") + low + (" giving examples." if lang == "en" else " ukitoa mifano.")) if ty == "essay"
                          else (("Explain how " if lang == "en" else "Eleza jinsi ") + low + (" works in detail." if lang == "en" else " inavyofanya kazi kwa kina.")),
                          "marks": mk,
                          "answer": ("Teacher judgement against rubric." if ty == "essay" else "A detailed correct explanation covering: " + ", ".join(kw[:4])),
                          "explain": "", "points": _points(kw, mk, lang), "auto": ty != "essay", "review": ty == "essay"})
        d["questions"] = (d.get("questions") or []) + extra
        _renumber_recompute(d)
    elif kind == "lesson_plan":
        d["flow"] = (d.get("flow") or []) + [{"step": ("Extension / Homework" if lang == "en" else "Upanuzi / Kazi ya nyumbani"),
                                              "duration": "10 min",
                                              "content": ("Investigate one real-world case of " + low + " and present findings next lesson." if lang == "en" else "Chunguza kesi moja halisi ya " + low + " na uwasilishe somo lijalo.")}]
        d["homework"] = ("Write a one-page summary of " + low + " including a labelled diagram and two exam-style questions." if lang == "en"
                         else "Andika muhtasari wa ukurasa mmoja wa " + low + " pamoja na mchoro wenye lebo na maswali mawili ya mtihani.")
    elif kind == "worksheet":
        n0 = len(d.get("tasks") or [])
        d["tasks"] = (d.get("tasks") or []) + [
            {"no": n0 + 1, "type": "apply", "prompt": ("List two ways " + low + " matters in your community." if lang == "en" else "Orodhesha njia mbili " + low + " inavyoleta faida jamii."), "lines": 3,
             "answer": "Any two valid, explained ways."},
            {"no": n0 + 2, "type": "challenge", "prompt": ("Design a simple investigation for " + low + "." if lang == "en" else "Buni uchunguzi rahisi wa " + low + "."), "lines": 4,
             "answer": "A workable method with variables identified."}]
    elif kind == "activity":
        d["steps"] = (d.get("steps") or []) + [{"step": ("Extension" if lang == "en" else "Upanuzi"), "duration": "10 min",
                                                "content": ("Groups design a follow-up investigation on " + low + "." if lang == "en" else "Vikundi vibuni uchunguzi wa ufuatiliaji kuhusu " + low + ".")}]
    elif kind == "marking_guide":
        d["rubric"] = (d.get("rubric") or []) + [{"name": ("Use of evidence / data" if lang == "en" else "Matumizi ya ushahidi / data"), "max": 2,
                                                  "descriptors": (["Strong, relevant evidence.", "Adequate evidence.", "Limited evidence.", "No evidence."] if lang == "en" else ["Ushahidi imara.", "Ushahidi wa kutosha.", "Ushahidi mdogo.", "Hakuna ushahidi."])}]
        d["total_marks"] = sum(r.get("max") or 0 for r in d["rubric"])
    d["expanded"] = True
    return d
def _apply_simplify(d):
    lang = d.get("language", "en")
    low = (d.get("topic") or "the topic").lower()
    parts = (_facts(low) or {}).get("parts") or [low, "process", "structure", "function"]
    kind = d.get("kind")
    if kind == "quiz":
        keep = [q for q in (d.get("questions") or []) if q.get("type") in ("mcq", "tf", "fill", "short")]
        keep = keep[:max(4, (len(keep) + 1) // 2)] or (d.get("questions") or [])[:4]
        for q in keep:
            q["marks"] = min(q.get("marks") or 1, 2)
            q["hint"] = ("Hint: recall the key term for " + low + "." if lang == "en" else "Dokezo: kumbuka istilahi muhimu ya " + low + ".")
        d["questions"] = keep
        d["word_bank"] = parts
        _renumber_recompute(d)
    elif kind == "lesson_plan":
        d["outcomes"] = [o.replace("Explain", "Describe").replace("Analyse", "Name").replace("Evaluate", "Match")
                         .replace("Eleza", "Eleza kwa ufupi").replace("Chambua", "Taja") for o in (d.get("outcomes") or [])]
        d["word_bank"] = parts
    elif kind == "worksheet":
        for t in (d.get("tasks") or []):
            t["lines"] = max(2, (t.get("lines") or 3) - 1)
        d["word_bank"] = parts
    d["simplified"] = True
    return d
'''
anchor = "class TeachingArtifactViewSet(viewsets.ModelViewSet):"
if "_apply_improve" not in src:
    src = src.replace(anchor, HELPERS.strip() + "\n\n\n" + anchor, 1)
TRANSFORM = r'''
    @action(detail=False, methods=["post"], url_path="transform")
    def transform(self, request):
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
            return Response({"detail": "Artifact content is not transformable."}, status=400)
        act = data.get("action")
        params = dict(lesson.get("_params") or {})
        params.setdefault("artifact_type", art.artifact_type)
        params.setdefault("topic", art.topic)
        if act == "save":
            from apps.resources.models import LearningResource, DocumentChunk
            lr_fields = {f.name for f in LearningResource._meta.fields}
            kwargs = {"institution": m.institution, "title": (lesson.get("title") or art.topic) + " (AI-generated)",
                      "status": "ready", "uploaded_by": request.user}
            for f, v in (("subject", lesson.get("subject")), ("grade_level", lesson.get("grade_level")),
                         ("curriculum", lesson.get("curriculum")), ("topic", lesson.get("topic")),
                         ("provenance_tier", "A"), ("license", "Original - AI-generated, school-owned"),
                         ("source_url", ""), ("attribution", "JIFUNZE AI Teacher Studio")):
                if f in lr_fields:
                    kwargs[f] = v or ""
            res, _ = LearningResource.objects.update_or_create(
                institution=m.institution, title=kwargs["title"],
                defaults={k: v for k, v in kwargs.items() if k not in ("institution", "title")})
            dc_fields = {f.name for f in DocumentChunk._meta.fields}
            DocumentChunk.objects.filter(resource=res).delete()
            blobs = [lesson.get("title", "")] + list(lesson.get("outcomes") or []) + \
                    [s.get("content", "") for s in (lesson.get("flow") or [])] + \
                    [q.get("stem", "") for q in (lesson.get("questions") or [])] + \
                    [lesson.get("assessment", ""), lesson.get("resources", ""), lesson.get("teacher_notes", "")]
            text = " ".join(x for x in blobs if x)
            for i in range(0, len(text), 900):
                ck = {"resource": res, "chunk_index": i // 900, "chunk_text": text[i:i + 900]}
                DocumentChunk.objects.create(**{k: v for k, v in ck.items() if k in dc_fields or k == "resource"})
            try:
                from apps.audit.models import AuditEvent
                AuditEvent.objects.create(institution=m.institution, actor=request.user, action="ARTIFACT_SAVED_TO_LIBRARY",
                                          resource_type="LearningResource", resource_id=str(res.id),
                                          metadata={"from_artifact": str(art.id)})
            except Exception:
                pass
            return Response({"saved": True, "resource_id": str(res.id), "title": kwargs["title"]})
        if act == "regenerate":
            params["variation"] = (params.get("variation") or 0) + 1
            new = BUILDERS.get(params.get("artifact_type"), build_lesson)(params)
        elif act == "translate":
            params["language"] = "sw" if (lesson.get("language") == "en") else "en"
            new = BUILDERS.get(params.get("artifact_type"), build_lesson)(params)
        elif act == "improve":
            new = _apply_improve(json.loads(json.dumps(lesson)))
        elif act == "expand":
            new = _apply_expand(json.loads(json.dumps(lesson)))
        elif act == "simplify":
            new = _apply_simplify(json.loads(json.dumps(lesson)))
        else:
            return Response({"detail": "Unknown action."}, status=400)
        new["_params"] = params
        content = json.dumps(new, indent=2)
        kwargs = dict(institution=m.institution, created_by=request.user,
                      artifact_type=params.get("artifact_type", art.artifact_type),
                      topic=params.get("topic", art.topic), content=content)
        existing = {f.name for f in TeachingArtifact._meta.fields}
        for f in ("grade_level", "curriculum", "subtopic", "week", "term", "subject"):
            if f in existing:
                kwargs[f] = (params.get(f) or "")
        newart = TeachingArtifact.objects.create(**kwargs)
        try:
            from apps.audit.models import AuditEvent
            AuditEvent.objects.create(institution=m.institution, actor=request.user, action="ARTIFACT_TRANSFORMED",
                                      resource_type="TeachingArtifact", resource_id=str(newart.id),
                                      metadata={"action": act, "from": str(art.id)})
        except Exception:
            pass
        return Response({"id": str(newart.id), "content": content, "action": act})
'''
if "url_path=\"transform\"" not in src:
    src = src + TRANSFORM
vp.write_text(src, encoding="utf-8")
tp = base / "templates/teacher_studio/studio.html"
html = tp.read_text(encoding="utf-8")
LAYER = r'''
<style>
  .aa-bar{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:.8rem;}
  .aa-btn{display:inline-flex;align-items:center;gap:.4rem;font-size:.78rem;font-weight:700;border-radius:.6rem;padding:.5rem .8rem;border:1px solid var(--line);background:#fff;color:var(--ink);cursor:pointer;transition:.15s;}
  .aa-btn:hover{background:var(--soft);border-color:var(--indigo);color:var(--indigo);transform:translateY(-1px);}
  .aa-btn:disabled{opacity:.55;cursor:wait;transform:none;}
  .aa-btn i,.aa-btn svg{width:14px;height:14px;}
  .hintbox{margin-top:.5rem;background:#EEF6FF;border:1px dashed #2563EB;border-radius:.5rem;padding:.45rem .65rem;font-size:.8rem;color:#1E40AF;}
  .enh-box{border-radius:.7rem;padding:.9rem 1rem;margin-top:1rem;font-size:.88rem;}
  .enh-red{background:#FEF2F2;border-left:4px solid var(--red);}
  .enh-ind{background:#EEF2FF;border-left:4px solid var(--indigo);}
</style>
<script>
(function(){
  var ACTIONS=[["regenerate","refresh-ccw","Regenerate"],["improve","sparkles","Improve"],["expand","plus-circle","Expand"],
               ["simplify","minus-circle","Simplify"],["translate","languages","Translate"],["save","bookmark","Save to Library"]];
  function toast(msg,tone){var t=document.createElement("div");t.textContent=msg;t.style.cssText="position:fixed;right:22px;bottom:22px;z-index:9999;padding:12px 18px;border-radius:12px;font:600 13px Inter,sans-serif;color:#fff;box-shadow:0 12px 30px -10px rgba(27,31,75,.6);background:"+(tone==="err"?"#DC2626":"#1B1F4B");document.body.appendChild(t);setTimeout(function(){t.remove();},2600);}
  function readBody(){return {artifact_type:document.getElementById("atype").value,topic:document.getElementById("topic").value,subtopic:document.getElementById("subtopic").value,grade_level:document.getElementById("grade").value,curriculum:document.getElementById("curr").value,week:document.getElementById("week").value,term:document.getElementById("term").value,duration:document.getElementById("duration").value,language:document.getElementById("language").value,count:document.getElementById("count").value,difficulty:document.getElementById("difficulty").value,mix:document.getElementById("mix").value};}
  function decorate(d){
    var doc=document.getElementById("doc");
    var old=document.getElementById("enh");if(old)old.remove();
    var html="";
    if(d.bloom&&d.bloom.length)html+='<div class="enh-box enh-ind"><b style="color:var(--indigo)">Bloom levels targeted:</b> '+d.bloom.map(function(x){return '<span class="wb">'+esc(x)+'</span>';}).join("")+'</div>';
    if(d.word_bank&&d.kind==="quiz")html+='<div class="enh-box enh-ind"><b style="color:var(--indigo)">Word bank:</b> '+d.word_bank.map(function(x){return '<span class="wb">'+esc(x)+'</span>';}).join("")+'</div>';
    if(d.misconceptions&&d.misconceptions.length)html+='<div class="enh-box enh-red"><b style="color:var(--red)">Common misconceptions to address:</b><ul style="margin:.4rem 0 0 1.1rem">'+d.misconceptions.map(function(x){return '<li>'+esc(x)+'</li>';}).join("")+'</ul></div>';
    if(d.homework)html+='<div class="enh-box enh-ind"><b style="color:var(--indigo)">Homework / extension:</b> '+esc(d.homework)+'</div>';
    if(html){var e=document.createElement("div");e.id="enh";e.className="no-print";e.innerHTML=html;doc.appendChild(e);}
    (d.questions||[]).forEach(function(q){
      var card=document.getElementById("qc"+q.no);if(!card||!q.hint)return;
      if(card.querySelector(".hintbox"))return;
      var stem=card.querySelector("p.font-medium");if(stem)stem.insertAdjacentHTML("afterend",'<div class="hintbox">'+esc(q.hint)+'</div>');
    });
  }
  function show(d,id){
    window.currentContent=JSON.stringify(d);window.currentLesson=d;window.currentArtifactId=id;window.lastMark=null;
    var doc=document.getElementById("doc");doc.classList.remove("show-answers");
    doc.innerHTML=renderAny(d,readBody());
    var sc=document.getElementById("scorecard");if(sc)sc.remove();
    document.getElementById("markBtn").classList.toggle("hidden",!(d&&d.kind==="quiz"));
    decorate(d);
    if(window.lucide)lucide.createIcons();
  }
  function bar(){
    if(document.getElementById("aaBar"))return;
    var out=document.getElementById("out");
    var b=document.createElement("div");b.id="aaBar";b.className="aa-bar no-print";
    b.innerHTML=ACTIONS.map(function(a){return '<button class="aa-btn" data-act="'+a[0]+'"><i data-lucide="'+a[1]+'"></i> '+a[2]+'</button>';}).join("");
    out.parentNode.insertBefore(b,out);
    b.addEventListener("click",function(ev){
      var btn=ev.target.closest(".aa-btn");if(!btn||!window.currentArtifactId)return;
      var act=btn.dataset.act;var label=btn.innerHTML;btn.disabled=true;btn.innerHTML="Working...";
      var token=document.querySelector("[name=csrfmiddlewaretoken]").value;
      fetch("/api/teacher/artifacts/transform/",{method:"POST",credentials:"same-origin",headers:{"X-CSRFToken":token,"Content-Type":"application/json"},body:JSON.stringify({artifact_id:window.currentArtifactId,action:act})})
      .then(function(r){return r.json().then(function(j){return {ok:r.ok,j:j};});})
      .then(function(res){
        if(!res.ok)throw new Error(res.j.detail||"Transform failed");
        if(act==="save"){toast("Saved to Library: "+res.j.title);return;}
        var d=JSON.parse(res.j.content);show(d,res.j.id);
        toast({regenerate:"Regenerated a fresh version",improve:"Improved with misconceptions, Bloom tags & explanations",expand:"Expanded with extra items & homework",simplify:"Simplified for foundation learners",translate:"Translated document"}[act]||"Updated");
      })
      .catch(function(e){toast(e.message,"err");})
      .finally(function(){btn.disabled=false;btn.innerHTML=label;if(window.lucide)lucide.createIcons();});
    });
    if(window.lucide)lucide.createIcons();
  }
  function hook(){
    bar();
    var f=document.getElementById("genform");
    f.addEventListener("submit",function(){setTimeout(bar,400);});
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",hook);else hook();
})();
</script>
'''
if "aaBar" not in html:
    i = html.rfind("{% endblock %}")
    html = html[:i] + LAYER + "\n" + html[i:]
    tp.write_text(html, encoding="utf-8")
print("AI ACTIONS TOOLBAR INSTALLED")
