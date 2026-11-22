from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
vp = base / "apps/teacher_studio/views.py"
src = vp.read_text(encoding="utf-8")
STATS = r'''
    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        from datetime import timedelta
        from django.utils import timezone
        m = Membership.objects.filter(user=request.user, is_active=True).first()
        if not m:
            return Response({"total": 0, "by_type": {}, "by_curr": [], "by_lang": {}, "days": [],
                             "marks_count": 0, "avg_percent": None, "pending_review": 0,
                             "transforms": {}, "saved": 0, "top_topics": [], "by_grade": {}})
        qs = TeachingArtifact.objects.filter(institution=m.institution)
        total = qs.count()
        by_type, by_curr, by_grade, by_lang, topics = {}, {}, {}, {}, {}
        for a in qs.order_by("-created_at")[:300]:
            by_type[a.artifact_type] = by_type.get(a.artifact_type, 0) + 1
            if a.curriculum:
                by_curr[a.curriculum] = by_curr.get(a.curriculum, 0) + 1
            if a.grade_level:
                by_grade[a.grade_level] = by_grade.get(a.grade_level, 0) + 1
            topics[a.topic] = topics.get(a.topic, 0) + 1
            try:
                lesson = json.loads(a.content)
                lg = lesson.get("language", "en")
                by_lang[lg] = by_lang.get(lg, 0) + 1
            except Exception:
                pass
        now = timezone.localtime()
        days = []
        for i in range(6, -1, -1):
            d = (now - timedelta(days=i)).date()
            days.append({"date": d.strftime("%a"), "count": qs.filter(created_at__date=d).count()})
        from apps.audit.models import AuditEvent
        marks = AuditEvent.objects.filter(institution=m.institution, action="QUIZ_AUTO_MARKED")
        pcts = [(e.metadata or {}).get("percent") for e in marks]
        pcts = [p for p in pcts if isinstance(p, (int, float))]
        avg = round(sum(pcts) / len(pcts), 1) if pcts else None
        pending = sum(len((e.metadata or {}).get("pending") or []) for e in marks)
        transforms = {}
        for e in AuditEvent.objects.filter(institution=m.institution, action="ARTIFACT_TRANSFORMED"):
            k = (e.metadata or {}).get("action") or "other"
            transforms[k] = transforms.get(k, 0) + 1
        saved = AuditEvent.objects.filter(institution=m.institution, action="ARTIFACT_SAVED_TO_LIBRARY").count()
        return Response({
            "total": total,
            "by_type": by_type,
            "by_curr": sorted(by_curr.items(), key=lambda kv: -kv[1])[:4],
            "by_grade": by_grade,
            "by_lang": by_lang,
            "days": days,
            "marks_count": len(pcts),
            "avg_percent": avg,
            "pending_review": pending,
            "transforms": transforms,
            "saved": saved,
            "top_topics": sorted(topics.items(), key=lambda kv: -kv[1])[:5],
        })
'''
if 'url_path="stats"' not in src:
    src = src + STATS
    vp.write_text(src, encoding="utf-8")
tp = base / "templates/teacher_studio/studio.html"
html = tp.read_text(encoding="utf-8")
DASH = r'''
<style>
  .kpi{background:var(--soft);border:1px solid var(--line);border-radius:.8rem;padding:.75rem .9rem;}
  .kpi p:first-child{font-size:.62rem;text-transform:uppercase;letter-spacing:.08em;color:var(--mut);font-weight:700;}
  .kpi .v{font-family:Manrope;font-weight:800;font-size:1.5rem;line-height:1.15;color:var(--indigo);}
  .kpi .s{font-size:.68rem;color:var(--mut);}
  .bar-row{display:flex;align-items:center;gap:.5rem;margin-top:.4rem;font-size:.72rem;}
  .bar-row .lbl{width:74px;color:var(--mut);font-weight:600;flex-shrink:0;}
  .bar-row .track{flex:1;background:#EDEBE3;border-radius:9999px;height:8px;overflow:hidden;}
  .bar-row .fill{height:100%;border-radius:9999px;background:linear-gradient(90deg,var(--indigo),#4550A6);}
  .bar-row .num{width:22px;text-align:right;font-weight:700;color:var(--indigo);}
  .spark{display:flex;align-items:flex-end;gap:5px;height:64px;}
  .spark .col{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:3px;}
  .spark .b{width:100%;border-radius:4px 4px 0 0;background:linear-gradient(180deg,var(--green),#0b8457);min-height:3px;}
  .spark .d{font-size:.6rem;color:var(--mut);font-weight:600;}
  .dash-h{font-family:Manrope;font-weight:800;color:var(--indigo);font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.35rem;}
</style>
<script>
(function(){
  function kpi(label,value,sub,color){
    return '<div class="kpi"><p>'+label+'</p><p class="v"'+(color?' style="color:'+color+'"':'')+'>'+value+'</p><p class="s">'+(sub||"")+'</p></div>';
  }
  function render(s){
    var strip=document.getElementById("dashStrip");if(!strip)return;
    var avg=s.avg_percent==null?"—":s.avg_percent+"%";
    var avgColor=s.avg_percent==null?"var(--mut)":(s.avg_percent>=65?"var(--green2)":(s.avg_percent>=50?"var(--amber)":"var(--red)"));
    var kpis=kpi("Materials generated",s.total||0,"all artifact types")+
             kpi("Auto-mark average",avg,s.marks_count?s.marks_count+" quizzes marked":"no quizzes marked yet",avgColor)+
             kpi("Pending review",s.pending_review||0,"items needing teacher judgement",s.pending_review?"var(--amber)":"var(--mut)")+
             kpi("Saved to library",s.saved||0,"reusable school resources")+
             kpi("AI refinements",Object.keys(s.transforms||{}).reduce(function(a,k){return a+s.transforms[k];},0),"regenerate / improve / expand / simplify / translate");
    var types=Object.keys(s.by_type||{});
    var maxT=Math.max.apply(null,types.map(function(k){return s.by_type[k];}).concat([1]));
    var bars=types.map(function(k){
      var v=s.by_type[k];
      return '<div class="bar-row"><span class="lbl">'+esc(k.replace("_"," "))+'</span><span class="track"><span class="fill" style="width:'+Math.round(100*v/maxT)+'%"></span></span><span class="num">'+v+'</span></div>';
    }).join("")||'<p style="color:var(--mut);font-size:.72rem">No materials yet.</p>';
    var maxD=Math.max.apply(null,(s.days||[]).map(function(d){return d.count;}).concat([1]));
    var spark=(s.days||[]).map(function(d){
      return '<div class="col" title="'+d.date+': '+d.count+'"><div class="b" style="height:'+Math.max(4,Math.round(52*d.count/maxD))+'px"></div><span class="d">'+d.date+'</span></div>';
    }).join("");
    var currs=(s.by_curr||[]).map(function(c){return '<span class="wb">'+esc(c[0])+' · '+c[1]+'</span>';}).join("")||'<span style="color:var(--mut);font-size:.72rem">—</span>';
    var langs=Object.keys(s.by_lang||{}).map(function(k){return '<span class="wb">'+(k==="sw"?"Kiswahili":"English")+' · '+s.by_lang[k]+'</span>';}).join("")||'<span style="color:var(--mut);font-size:.72rem">—</span>';
    var tops=(s.top_topics||[]).map(function(t){return '<span class="wb">'+esc(t[0])+' · '+t[1]+'</span>';}).join("")||'<span style="color:var(--mut);font-size:.72rem">—</span>';
    strip.innerHTML=
      '<div class="flex items-center justify-between mb-3"><h3 style="font-family:Manrope;font-weight:800;color:var(--indigo);font-size:.95rem;display:flex;align-items:center;gap:.45rem"><i data-lucide="layout-dashboard"></i> Studio analytics</h3><button id="dashRefresh" class="aa-btn" style="padding:.35rem .6rem"><i data-lucide="refresh-cw"></i></button></div>'+
      '<div class="grid grid-cols-2 md:grid-cols-5 gap-3">'+kpis+'</div>'+
      '<div class="grid md:grid-cols-3 gap-5 mt-4">'+
        '<div><p class="dash-h">By artifact type</p>'+bars+'</div>'+
        '<div><p class="dash-h">Last 7 days</p><div class="spark">'+spark+'</div></div>'+
        '<div><p class="dash-h">Curriculum mix</p><div>'+currs+'</div><p class="dash-h" style="margin-top:.6rem">Language</p><div>'+langs+'</div><p class="dash-h" style="margin-top:.6rem">Top topics</p><div>'+tops+'</div></div>'+
      '</div>';
    var rb=document.getElementById("dashRefresh");if(rb)rb.onclick=load;
    if(window.lucide)lucide.createIcons();
  }
  function load(){
    fetch("/api/teacher/artifacts/stats/",{credentials:"same-origin"}).then(function(r){return r.json();}).then(render).catch(function(){});
  }
  function mount(){
    if(document.getElementById("dashStrip"))return;
    var err=document.getElementById("err");if(!err)return;
    var strip=document.createElement("div");
    strip.id="dashStrip";strip.className="jf-card no-print";
    strip.style.cssText="padding:1rem 1.2rem;margin-bottom:1.2rem";
    err.parentNode.insertBefore(strip,err);
    load();
    setInterval(load,30000);
    document.getElementById("genform").addEventListener("submit",function(){setTimeout(load,2500);});
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount);else mount();
})();
</script>
'''
if "dashStrip" not in html:
    i = html.rfind("{% endblock %}")
    html = html[:i] + DASH + "\n" + html[i:]
    tp.write_text(html, encoding="utf-8")
print("STUDIO DASHBOARD STRIP INSTALLED")
