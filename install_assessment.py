from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
vp = base / "apps/teacher_studio/views.py"
src = vp.read_text(encoding="utf-8")
idx = src.index("def _norm(s):")
TAIL = r'''def _norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\.\-/ ]+", " ", str(s or "").lower())).strip()
def _grade_band(pct):
    if pct >= 80:
        return "A · Exceeding expectation"
    if pct >= 65:
        return "B · Meeting expectation"
    if pct >= 50:
        return "C · Approaching expectation"
    if pct >= 40:
        return "D · Below expectation"
    return "E · Needs support"
def _advice(pct, pending, lang):
    if lang == "sw":
        if pct >= 80:
            return ["Bora sana — endeleza kwa maswali ya changamoto zaidi."]
        if pct >= 65:
            return ["Nzuri — fanya marejeo madogo ya dhana zilizokosewa."]
        if pct >= 50:
            return ["Inakaribia — rudia mada hii kwa mifano zaidi ya vitendo."]
        return ["Rudia mafundisho ya msingi ya mada hii kwa msaada wa mwalimu."]
    if pct >= 80:
        return ["Excellent mastery — extend with challenge questions and peer teaching."]
    if pct >= 65:
        return ["Good grasp — brief revision of the missed concepts will close the gap."]
    if pct >= 50:
        return ["Approaching competence — reteach the topic with worked examples before retesting."]
    return ["Foundational gaps — schedule supported reteaching and a diagnostic retake."]
def grade_question(q, ans, lang="en"):
    t = q.get("type")
    marks = float(q.get("marks") or 0)
    awarded, status, fb, conf = 0.0, "wrong", "", 1.0
    if t == "mcq":
        try:
            sel = int(ans)
        except (TypeError, ValueError):
            sel = -1
        if sel == q.get("correct"):
            awarded, status, fb = marks, "correct", "Correct option selected."
        elif sel < 0:
            status, fb = "blank", "No option selected."
        else:
            fb = "Correct answer: " + str(q.get("answer"))
    elif t == "multi":
        correct = set(q.get("correct_multi") or [])
        try:
            sel = set(int(x) for x in (ans or []))
        except (TypeError, ValueError):
            sel = set()
        if not sel:
            status, fb = "blank", "No options selected."
        else:
            hits, misses = len(sel & correct), len(sel - correct)
            per = marks / max(1, len(correct))
            awarded = max(0.0, round((hits - misses) * per, 2))
            status = "correct" if awarded >= marks else ("partial" if awarded > 0 else "wrong")
            fb = "%d correct, %d incorrect selections." % (hits, misses)
    elif t == "tf":
        if ans in (None, ""):
            status, fb = "blank", "No choice made."
        else:
            truth = str(ans).lower() in ("true", "1", "yes")
            if truth == bool(q.get("tf_answer")):
                awarded, status, fb = marks, "correct", "Correct judgement."
            else:
                fb = "Correct answer: " + str(q.get("answer"))
    elif t == "numeric":
        spec = q.get("numeric") or {}
        m = re.search(r"-?\d+(?:\.\d+)?", str(ans or ""))
        if not m:
            status, fb = "blank", "No numeric answer given."
        else:
            val = float(m.group())
            if abs(val - float(spec.get("value", 0))) <= float(spec.get("tol", 0)) + 1e-9:
                awarded, status, fb = marks, "correct", "Correct value (method + answer marks)."
            else:
                awarded, status, fb = round(marks / 2, 2), "partial", "Method credit only. Expected " + str(spec.get("value")) + " " + str(spec.get("unit") or "")
    elif t == "fill":
        vals = ans if isinstance(ans, list) else [ans]
        accept = q.get("blanks_accept") or []
        hits = 0
        for i, group in enumerate(accept):
            got = _norm(vals[i]) if i < len(vals) else ""
            if got and any(got == _norm(a) or _norm(a) in got for a in group):
                hits += 1
        awarded = round(marks * hits / max(1, len(accept)), 2)
        status = "blank" if not any(vals) else ("correct" if hits == len(accept) else ("partial" if hits else "wrong"))
        fb = "%d of %d blanks correct." % (hits, len(accept))
    elif t == "match":
        pairs = q.get("pairs") or []
        vals = ans if isinstance(ans, list) else []
        hits = 0
        for i, p in enumerate(pairs):
            got = _norm(vals[i]) if i < len(vals) else ""
            if got and got == _norm(p.get("meaning")):
                hits += 1
        awarded = round(marks * hits / max(1, len(pairs)), 2)
        status = "blank" if not any(vals) else ("correct" if hits == len(pairs) else ("partial" if hits else "wrong"))
        fb = "%d of %d matches correct." % (hits, len(pairs))
    elif t == "diagram":
        expected = q.get("labels_expected") or []
        vals = ans if isinstance(ans, list) else []
        hits = 0
        for i, exp in enumerate(expected):
            got = _norm(vals[i]) if i < len(vals) else ""
            if got and (got == _norm(exp) or _norm(exp) in got):
                hits += 1
        awarded = round(marks * hits / max(1, len(expected)), 2)
        status = "blank" if not any(vals) else ("correct" if hits == len(expected) else ("partial" if hits else "wrong"))
        fb = "%d of %d labels correct." % (hits, len(expected))
    elif t == "essay":
        text = str(ans or "")
        words = len(text.split())
        low = _norm(text)
        pts = q.get("points") or []
        hit = sum(1 for p in pts if any(_norm(k) and _norm(k) in low for k in (p.get("keywords") or [])))
        kw_cov = hit / max(1, len(pts))
        struct = sum(1 for w in ("because", "therefore", "example", "first", "second", "however", "kwa sababu", "kwa hivyo", "mfano") if w in low) / 5.0
        length = min(1.0, words / 120.0)
        prov = round(marks * (0.45 * kw_cov + 0.30 * struct + 0.25 * length), 2)
        awarded, status, conf = prov, "review", 0.55
        fb = ("Provisional %s/%s from rubric (content %.0f%%, structure %.0f%%, development %.0f%%). Confirm with teacher judgement."
              % (prov, int(marks), kw_cov * 100, struct * 100, length * 100))
        if not words:
            awarded, status, fb = 0.0, "blank", "No response written."
    elif t in ("short", "structured"):
        text = _norm(ans)
        pts = q.get("points") or []
        if not text:
            status, fb = "blank", "No response written."
        else:
            hit_labels = []
            for p in pts:
                if any(_norm(k) and _norm(k) in text for k in (p.get("keywords") or [])):
                    awarded += float(p.get("mark") or 0)
                    hit_labels.append(p.get("label"))
            awarded = round(min(awarded, marks), 2)
            status = "correct" if awarded >= marks else ("partial" if awarded > 0 else "review")
            fb = ("Credit for: " + ", ".join(hit_labels)) if hit_labels else "No marking points detected — teacher review advised."
            conf = 0.9 if hit_labels else 0.5
            if q.get("review"):
                fb += " (keyword match — confirm with teacher judgement)"
    else:
        status, fb, conf = "review", "Extended response — requires teacher judgement against the rubric.", 0.5
    return {"no": q.get("no"), "type": t, "marks": marks, "awarded": awarded, "status": status,
            "feedback": fb, "expected": q.get("answer"), "points": q.get("points") or [], "confidence": conf}
class TeachingArtifactViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        m = Membership.objects.filter(user=self.request.user, is_active=True).first()
        return TeachingArtifact.objects.filter(institution=m.institution) if m else TeachingArtifact.objects.none()
    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        data = request.data if isinstance(request.data, dict) else {}
        m = Membership.objects.filter(user=request.user, is_active=True).first()
        if not m:
            return Response({"detail": "You must belong to an institution."}, status=400)
        atype = data.get("artifact_type", "lesson_plan")
        topic = (data.get("topic") or "Lesson").strip()
        content = json.dumps(BUILDERS.get(atype, build_lesson)(data), indent=2)
        kwargs = dict(institution=m.institution, created_by=request.user, artifact_type=atype, topic=topic, content=content)
        existing = {f.name for f in TeachingArtifact._meta.fields}
        for f in ("grade_level", "curriculum", "subtopic", "week", "term", "subject"):
            if f in existing:
                kwargs[f] = (data.get(f) or "")
        artifact = TeachingArtifact.objects.create(**kwargs)
        try:
            from apps.audit.models import AuditEvent
            AuditEvent.objects.create(institution=m.institution, actor=request.user, action="TEACHER_ARTIFACT_GENERATED",
                                      resource_type="TeachingArtifact", resource_id=str(artifact.id), metadata={"type": atype})
        except Exception:
            pass
        return Response({"id": str(artifact.id), "content": content, "topic": topic, "artifact_type": atype}, status=201)
    @action(detail=False, methods=["post"], url_path="automark")
    def automark(self, request):
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
            return Response({"detail": "Artifact is not a markable quiz."}, status=400)
        questions = lesson.get("questions") or []
        if not questions:
            return Response({"detail": "This artifact has no questions."}, status=400)
        lang = lesson.get("language", "en")
        answers = data.get("answers") or {}
        results = [grade_question(q, answers.get(str(q.get("no")), answers.get(q.get("no"))), lang) for q in questions]
        total = sum(r["marks"] for r in results)
        awarded = round(sum(r["awarded"] for r in results), 2)
        pending = [r["no"] for r in results if r["status"] == "review"]
        pct = round(100.0 * awarded / total, 1) if total else 0.0
        by_type = {}
        for r in results:
            e = by_type.setdefault(r["type"], {"marks": 0.0, "awarded": 0.0})
            e["marks"] += r["marks"]; e["awarded"] += r["awarded"]
        report = {
            "total_marks": total, "awarded": awarded, "percentage": pct, "band": _grade_band(pct),
            "pending": pending, "results": results, "advice": _advice(pct, pending, lang),
            "by_type": {k: {"marks": v["marks"], "awarded": round(v["awarded"], 2),
                            "pct": round(100.0 * v["awarded"] / v["marks"], 1) if v["marks"] else 0.0} for k, v in by_type.items()},
            "topic": art.topic, "grade_level": lesson.get("grade_level", ""), "curriculum": lesson.get("curriculum", ""),
        }
        try:
            from apps.audit.models import AuditEvent
            AuditEvent.objects.create(institution=m.institution, actor=request.user, action="QUIZ_AUTO_MARKED",
                                      resource_type="TeachingArtifact", resource_id=str(art.id),
                                      metadata={"awarded": awarded, "total": total, "percent": pct,
                                                "band": report["band"], "pending": pending, "topic": art.topic})
        except Exception:
            pass
        return Response(report)
    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        m = Membership.objects.filter(user=request.user, is_active=True).first()
        if not m:
            return Response([])
        from apps.audit.models import AuditEvent
        rows = []
        for e in AuditEvent.objects.filter(institution=m.institution, action="QUIZ_AUTO_MARKED").order_by("-id")[:12]:
            meta = e.metadata or {}
            art = TeachingArtifact.objects.filter(id=e.resource_id).first()
            rows.append({
                "date": e.created_at.strftime("%d %b %Y, %H:%M") if e.created_at else "",
                "topic": meta.get("topic") or (art.topic if art else ""),
                "awarded": meta.get("awarded", 0), "total": meta.get("total", 0),
                "percent": meta.get("percent", 0), "band": meta.get("band", ""),
            })
        return Response(rows)
'''
vp.write_text(src[:idx] + TAIL, encoding="utf-8")
tp = base / "templates/teacher_studio/studio.html"
html = tp.read_text(encoding="utf-8")
LAYER = r'''
<style>
  .aa-card{background:var(--card);border:1px solid var(--line);border-radius:1rem;box-shadow:0 6px 18px -8px rgba(27,31,75,.14);padding:1.1rem 1.2rem;margin-bottom:1rem;}
  .aa-card h4{font-family:Manrope;font-weight:800;color:var(--indigo);font-size:.95rem;margin-bottom:.6rem;display:flex;align-items:center;gap:.45rem;}
  .aa-table{width:100%;border-collapse:collapse;font-size:.8rem;}
  .aa-table th,.aa-table td{border:1px solid var(--line);padding:.45rem .55rem;text-align:left;vertical-align:top;}
  .aa-table th{background:var(--indigo);color:#fff;font-family:Manrope;}
  .aa-table tr:nth-child(even) td{background:var(--soft);}
  .pill{display:inline-block;font-size:.66rem;font-weight:800;padding:.15rem .5rem;border-radius:9999px;}
  .pill.correct{background:#DCFCE7;color:#166534;} .pill.partial{background:#FEF3C7;color:#92400E;}
  .pill.wrong{background:#FEE2E2;color:#991B1B;} .pill.review{background:#E0E7FF;color:#3730A3;} .pill.blank{background:#F1F5F9;color:#475569;}
  .hist{display:flex;justify-content:space-between;gap:.6rem;padding:.5rem .65rem;border:1px solid var(--line);border-radius:.55rem;margin-top:.45rem;font-size:.8rem;background:#fff;}
  .hist:hover{background:var(--soft);}
</style>
<script>
(function(){
  function el(html){var d=document.createElement("div");d.innerHTML=html.trim();return d.firstChild;}
  function ensurePanels(){
    if(!document.getElementById("reportPanel")){
      var doc=document.getElementById("doc");
      var rp=el('<div id="reportPanel" class="no-print" style="margin-top:1.6rem"></div>');
      doc.appendChild(rp);
    }
    if(!document.getElementById("histPanel")){
      var out=document.getElementById("out");
      var hp=el('<div id="histPanel" class="aa-card no-print" style="display:none"><h4><i data-lucide="history"></i> Assessment history</h4><div id="histList"></div></div>');
      out.parentNode.insertBefore(hp,out);
    }
    if(!document.getElementById("repBtn")){
      var bar=document.getElementById("printBtn").parentNode;
      var b=el('<button id="repBtn" class="jf-btn ghost flex-1 no-print"><i data-lucide="file-bar-chart-2"></i> Report PDF</button>');
      bar.insertBefore(b,document.getElementById("printBtn"));
      b.onclick=reportPdf;
    }
    loadHistory();
    if(window.lucide)lucide.createIcons();
  }
  function loadHistory(){
    fetch("/api/teacher/artifacts/history/",{credentials:"same-origin"}).then(function(r){return r.json();}).then(function(rows){
      var panel=document.getElementById("histPanel");if(!panel)return;
      if(!rows||!rows.length){panel.style.display="none";return;}
      panel.style.display="block";
      document.getElementById("histList").innerHTML=rows.map(function(x){
        return '<div class="hist"><span><b>'+esc(x.topic||"Quiz")+'</b> · '+esc(x.date)+'</span><span>'+x.awarded+'/'+x.total+' ('+x.percent+'%)</span><span class="pill '+(x.percent>=65?"correct":(x.percent>=50?"partial":"wrong"))+'">'+esc(x.band)+'</span></div>';
      }).join("");
    }).catch(function(){});
  }
  function renderReport(){
    ensurePanels();
    var r=window.lastMark;if(!r)return;
    var L=(window.I18N&&window.I18N[(window.currentLesson&&window.currentLesson.language==="sw")?"sw":"en"])||window.I18N.en;
    var rows=(r.results||[]).map(function(x){
      return '<tr><td>'+x.no+'</td><td>'+(window.TYPE_LABEL[x.type]||x.type)+'</td><td>'+x.marks+'</td><td><b>'+x.awarded+'</b></td><td><span class="pill '+x.status+'">'+x.status+'</span></td><td>'+esc(x.feedback)+'</td></tr>';
    }).join("");
    var types=Object.keys(r.by_type||{}).map(function(k){
      var v=r.by_type[k];return '<tr><td>'+(window.TYPE_LABEL[k]||k)+'</td><td>'+v.awarded+' / '+v.marks+'</td><td>'+v.pct+'%</td></tr>';
    }).join("");
    var adv=(r.advice||[]).map(function(a){return '<li>'+esc(a)+'</li>';}).join("");
    document.getElementById("reportPanel").innerHTML=
      '<div class="aa-card"><h4><i data-lucide="clipboard-check"></i> Auto-assessment report</h4>'+
      '<div style="overflow-x:auto"><table class="aa-table"><tr><th>'+L.q+'</th><th>Type</th><th>Marks</th><th>Awarded</th><th>Status</th><th>Feedback</th></tr>'+rows+'</table></div></div>'+
      '<div class="grid md:grid-cols-2 gap-4"><div class="aa-card"><h4><i data-lucide="pie-chart"></i> Performance by question type</h4>'+
      '<table class="aa-table"><tr><th>Type</th><th>Awarded</th><th>%</th></tr>'+types+'</table></div>'+
      '<div class="aa-card"><h4><i data-lucide="lightbulb"></i> Recommended next steps</h4><ul style="margin:0;padding-left:1.1rem;font-size:.85rem;color:var(--mut)">'+adv+'</ul></div></div>';
    if(window.lucide)lucide.createIcons();
  }
  function reportPdf(){
    var r=window.lastMark;if(!r||!window.jspdf){window.print();return;}
    var doc=new window.jspdf.jsPDF({unit:"mm",format:"a4",compress:true});
    var W=210,M=16,CW=W-2*M,y=0;
    doc.setFillColor(27,31,75);doc.rect(0,0,W,26,"F");
    doc.setFillColor(201,162,39);doc.rect(0,26,W,1.4,"F");
    doc.setTextColor(255,255,255);doc.setFont("helvetica","bold");doc.setFontSize(8.5);
    doc.text("JIFUNZE AI  ·  AUTO-ASSESSMENT REPORT",M,10);
    doc.setFontSize(15);doc.text(String((window.currentLesson&&window.currentLesson.title)||"Assessment").slice(0,70),M,19);
    y=36;
    doc.setTextColor(15,23,42);doc.setFontSize(10);doc.setFont("helvetica","bold");
    doc.text("Score: "+r.awarded+" / "+r.total_marks+"   ("+r.percentage+"%)",M,y);y+=6;
    doc.text("Performance: "+r.band,M,y);y+=6;
    doc.text("Teacher review required: "+(r.pending.length?r.pending.length+" item(s)":"None"),M,y);y+=6;
    doc.text("Date: "+new Date().toLocaleString(),M,y);y+=10;
    if(typeof doc.autoTable==="function"){
      doc.autoTable({startY:y,margin:{left:M,right:M,top:18},
        head:[["Q","Type","Marks","Awarded","Status","Feedback"]],
        body:(r.results||[]).map(function(x){return [x.no,(window.TYPE_LABEL[x.type]||x.type),x.marks,x.awarded,x.status,String(x.feedback).slice(0,90)];}),
        styles:{font:"helvetica",fontSize:7.6,cellPadding:2.2,lineColor:[228,225,214],lineWidth:0.2,valign:"top"},
        headStyles:{fillColor:[27,31,75],textColor:255,fontStyle:"bold"},
        alternateRowStyles:{fillColor:[246,244,236]},
        columnStyles:{0:{cellWidth:9},2:{cellWidth:14},3:{cellWidth:16},4:{cellWidth:18}}});
      y=(doc.lastAutoTable?doc.lastAutoTable.finalY:y)+8;
    }
    doc.setFontSize(9);doc.setFont("helvetica","bold");doc.setTextColor(27,31,75);
    doc.text("RECOMMENDED NEXT STEPS",M,y);y+=5;
    doc.setFont("helvetica","normal");doc.setTextColor(100,116,139);
    (r.advice||[]).forEach(function(a){var ls=doc.splitTextToSize(a,CW);ls.forEach(function(l){doc.text(l,M,y);y+=4.6;});});
    var n=doc.getNumberOfPages();
    for(var p=1;p<=n;p++){doc.setPage(p);doc.setDrawColor(228,225,214);doc.line(M,283,W-M,283);doc.setFontSize(7.5);doc.setTextColor(100,116,139);doc.text("Generated by JIFUNZE AI auto-assessment engine",M,288);doc.text("Page "+p+" of "+n,W-M,288,{align:"right"});}
    doc.save("assessment_report.pdf");
  }
  function wrap(){
    var mb=document.getElementById("markBtn");if(!mb||mb.__wrapped)return;mb.__wrapped=true;
    var orig=mb.onclick;
    mb.onclick=function(){var self=this,args=arguments;
      return Promise.resolve(orig?orig.apply(self,args):null).then(function(){setTimeout(renderReport,60);loadHistory();});};
    ensurePanels();
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",wrap);else wrap();
  document.getElementById("genform").addEventListener("submit",function(){setTimeout(ensurePanels,400);});
})();
</script>
'''
if "AUTO-ASSESS LAYER" not in html and "reportPanel" not in html:
    i = html.rfind("{% endblock %}")
    html = html[:i] + LAYER + "\n" + html[i:]
    tp.write_text(html, encoding="utf-8")
print("AUTO-MARKING SCHEME + AUTO-ASSESSMENT LAYER INSTALLED")
