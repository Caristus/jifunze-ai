import re
from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
def w(rel, text):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
# ============ A. RETENTION POLICY ============
ip = base / "apps/institutions/models.py"
im = ip.read_text(encoding="utf-8")
if "retention_days" not in im:
    lines = im.splitlines(keepends=True)
    for i, l in enumerate(lines):
        if l.strip().startswith("country = models.CharField(") or l.strip().startswith("name = models.CharField("):
            indent = l[:len(l) - len(l.lstrip())]
            lines.insert(i + 1, indent + 'retention_days = models.IntegerField(default=365, help_text="Days to retain audit and conversation data")\n')
            break
    ip.write_text("".join(lines), encoding="utf-8")
gm = base / "apps/governance/management/commands"
gm.mkdir(parents=True, exist_ok=True)
(base / "apps/governance/management/__init__.py").touch(exist_ok=True)
(gm / "__init__.py").touch(exist_ok=True)
w("apps/governance/management/commands/apply_retention.py", '''from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.audit.models import AuditEvent
from apps.institutions.models import Institution
from apps.learning.models import Conversation, Message
def fields(model):
    return {f.name for f in model._meta.fields}
class Command(BaseCommand):
    help = "Delete audit and conversation data older than each institution's retention_days."
    def handle(self, *args, **o):
        now = timezone.localtime()
        for inst in Institution.objects.all():
            days = getattr(inst, "retention_days", 365) or 365
            cutoff = now - timedelta(days=days)
            af = fields(AuditEvent)
            aq = AuditEvent.objects.filter(institution=inst)
            if "created_at" in af:
                aq = aq.filter(created_at__lt=cutoff)
            a_del = aq.delete()[0]
            cf = fields(Conversation)
            cq = Conversation.objects.filter(institution=inst)
            if "created_at" in cf:
                cq = cq.filter(created_at__lt=cutoff)
            c_del = cq.delete()[0]
            mf = fields(Message)
            m_del = 0
            if "conversation" in mf:
                mq = Message.objects.filter(conversation__institution=inst)
                if "created_at" in mf:
                    mq = mq.filter(created_at__lt=cutoff)
                m_del = mq.delete()[0]
            try:
                AuditEvent.objects.create(institution=inst, actor=None, action="RETENTION_APPLIED",
                                          resource_type="Institution", resource_id=str(inst.id),
                                          metadata={"days": days, "audit": a_del, "conversations": c_del, "messages": m_del})
            except Exception:
                pass
            self.stdout.write(self.style.SUCCESS("%s: retention %dd -> audit=%d conversations=%d messages=%d" % (inst.name, days, a_del, c_del, m_del)))
''')
# ============ D. SEMANTIC SEARCH ============
w("apps/learning/semantic.py", '''import hashlib
import math
import re
DIM = 64
def _tokens(text):
    return [w for w in re.sub(r"[^a-z0-9 ]", " ", (text or "").lower()).split() if len(w) > 2]
def encode(text, dim=DIM):
    """Deterministic hashed bag-of-words vector. Swap for sentence-transformers / pgvector in production."""
    v = [0.0] * dim
    for tok in _tokens(text):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        v[h % dim] += 1.0 + ((h >> 8) % 7) / 7.0
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [round(x / norm, 5) for x in v]
def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))
def pgvector_available():
    from django.db import connection
    if connection.vendor != "postgresql":
        return False
    try:
        with connection.cursor() as c:
            c.execute("SELECT 1 FROM pg_extension WHERE extname='vector'")
            return c.fetchone() is not None
    except Exception:
        return False
def semantic_search(institution, query, k=8):
    from apps.resources.models import DocumentChunk
    qv = encode(query)
    rows = []
    qs = DocumentChunk.objects.filter(resource__institution=institution).select_related("resource")
    for c in qs[:500]:
        emb = c.embedding if isinstance(c.embedding, list) else None
        if not emb:
            continue
        rows.append((cosine(qv, emb), c))
    rows.sort(key=lambda x: -x[0])
    out = []
    for score, c in rows[:k]:
        out.append({"score": round(score, 3), "title": c.resource.title,
                    "subject": getattr(c.resource, "subject", ""), "grade": getattr(c.resource, "grade_level", ""),
                    "chunk": (c.chunk_text or "")[:300]})
    return out
''')
w("apps/resources/semantic_views.py", '''from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.institutions.models import Membership
from apps.learning.semantic import semantic_search
@login_required(login_url="/accounts/login/")
def search(request):
    q = (request.GET.get("q") or "").strip()
    m = Membership.objects.filter(user=request.user, is_active=True).first()
    if not m or not q:
        return JsonResponse({"results": []})
    return JsonResponse({"results": semantic_search(m.institution, q, 8)})
''')
w("apps/learning/progress_views.py", '''from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from apps.institutions.models import Membership
from apps.learning.models import Conversation, Message, MessageSource
def fields(model):
    return {f.name for f in model._meta.fields}
@login_required(login_url="/accounts/login/")
def progress(request):
    m = Membership.objects.filter(user=request.user, is_active=True).first()
    if not m:
        return JsonResponse({"sessions": 0, "messages": 0, "sources": 0, "days": [], "topics": []})
    cf = fields(Conversation)
    convs = Conversation.objects.filter(institution=m.institution)
    if "user" in cf:
        convs = convs.filter(user=request.user)
    mf = fields(Message)
    msgs = Message.objects.filter(conversation__in=convs)
    learner = msgs.filter(role="user") if "role" in mf else msgs
    sources = MessageSource.objects.filter(message__in=msgs).count() if "message" in fields(MessageSource) else 0
    now = timezone.localtime()
    days = []
    for i in range(6, -1, -1):
        d = (now - timedelta(days=i)).date()
        n = 0
        if "created_at" in cf:
            n += convs.filter(created_at__date=d).count()
        if "created_at" in mf:
            n += msgs.filter(created_at__date=d).count()
        days.append({"date": d.strftime("%a"), "count": n})
    topics = []
    if "title" in cf:
        topics = [t for t in convs.values_list("title", flat=True) if t][:6]
    return JsonResponse({"sessions": convs.count(), "messages": learner.count(), "sources": sources,
                         "active_days": sum(1 for d in days if d["count"]), "days": days, "topics": topics})
''')
up = base / "config/urls.py"
uc = up.read_text(encoding="utf-8")
if "progress_views" not in uc:
    uc = "from apps.learning import progress_views\nfrom apps.resources import semantic_views\n" + uc
    uc = re.sub(r'(path\("library/",[^)]*\),)',
                r'\1\n    path("api/learn/progress/", progress_views.progress),\n    path("api/resources/semantic_search/", semantic_views.search),',
                uc, count=1)
    up.write_text(uc, encoding="utf-8")
# ============ C. SCHEME OF WORK + REVISION NOTES BUILDERS ============
vp = base / "apps/teacher_studio/views.py"
vs = vp.read_text(encoding="utf-8")
NEW_BUILDERS = r'''
def build_scheme(data):
    d = _base(data, "scheme_of_work")
    low, lang, b = d["topic"].lower(), d["language"], d["band"]
    n = _count(data)
    facts = _facts(low)
    prog = (["Utangulizi na tathmini ya msingi", "Dhana kuu na istilahi", "Mazoezi ya kuongozwa na matumizi",
             "Matumizi papana na uchunguzi", "Tathmini, maona na marejeo"] if lang == "sw" else
            ["Introduction and baseline assessment", "Core concepts and terminology", "Guided practice and application",
             "Extended application and investigation", "Assessment, feedback and revision"])
    subs = ((facts["parts"] if facts else []) + prog)
    verbs = {"early": ["Identify", "Describe"], "primary": ["Describe", "Demonstrate"],
             "junior": ["Explain", "Apply"], "senior": ["Analyse", "Evaluate"]}[b]
    weeks = []
    for i in range(n):
        sub = subs[i % len(subs)]
        weeks.append({
            "week": i + 1, "subtopic": sub.title(), "lessons": 3,
            "objectives": ["%s %s in the context of %s." % (verbs[0], sub.lower(), low),
                           "%s the relationship between %s and %s." % (verbs[1], sub.lower(), low)],
            "activities": [("Group discussion and concept mapping of %s." % sub.lower()) if lang == "en" else ("Mjadala wa kikundi na ramani ya dhana ya %s." % sub.lower()),
                           ("Practical/task-based practice on %s." % sub.lower()) if lang == "en" else ("Mazoezi ya vitendo kuhusu %s." % sub.lower())],
            "assessment": ("Exit ticket + weekly quiz on %s." % sub.lower()) if lang == "en" else ("Karatasi ya kutoka + jaribio la wiki kuhusu %s." % sub.lower()),
            "resources": S[lang]["res"],
        })
    d["weeks"] = weeks
    d["coverage"] = ("100%% of %s spread across %d teaching weeks" % (low, n)) if lang == "en" else ("100%% ya %s ikisambazwa kwa wiki %d za mafundisho" % (low, n))
    d["notes"] = S[lang]["notes"]
    return d
def build_revision(data):
    d = _base(data, "revision_notes")
    low, lang = d["topic"].lower(), d["language"]
    facts = _facts(low)
    key_terms = facts["parts"] if facts else ([low] + ["definition", "structure", "function", "application"])
    d["key_terms"] = key_terms
    d["summary"] = (("%s is understood through: %s." % (low.title(), ", ".join((facts["kw"] if facts else key_terms)[:6]))) if lang == "en"
                    else ("%s inaeleweka kupitia: %s." % (low.title(), ", ".join((facts["kw"] if facts else key_terms)[:6]))))
    d["key_points"] = ([("Define %s precisely using key terms." % low),
                        ("Explain the role of each of: %s." % ", ".join(key_terms[:4])),
                        ("Apply %s to one real-life example." % low),
                        ("Practise past-paper questions under timed conditions.")] if lang == "en" else
                       [("Fafanua %s kwa usahihi kwa istilahi muhimu." % low),
                        ("Eleza dhima ya kila moja ya: %s." % ", ".join(key_terms[:4])),
                        ("Tumia %s katika mfano mmoja halisi." % low),
                        ("Fanya maswali ya mitihani iliyopita kwa muda uliopangwa.")])
    num = facts.get("numeric") if facts else None
    d["worked_example"] = (("%s Answer: %s." % (num["q"], num["answer"])) if num else
                           ("Method: (1) write what is asked, (2) list known facts, (3) apply the rule, (4) check units and reasonableness." if lang == "en"
                            else "Mbinu: (1) andika kinachoulizwa, (2) orodhesha ukweli unaojulikana, (3) tumia kanuni, (4) hakiki vitengo."))
    d["exam_questions"] = [
        {"q": ("Define %s." % low) if lang == "en" else ("Fafanua %s." % low), "a": ("A precise definition using: %s." % ", ".join(key_terms[:3]))},
        {"q": ("State two applications of %s." % low) if lang == "en" else ("Taja matumizi mawili ya %s." % low), "a": ("Any two valid, explained applications.")},
        {"q": ("Explain %s step by step." % low) if lang == "en" else ("Eleza %s hatua kwa hatua." % low), "a": ("Ordered explanation covering the key points.")},
    ]
    d["mnemonic"] = "".join(wd[0].upper() for wd in key_terms[:6]) or "REVISE"
    d["checklist"] = ([("I can define %s without notes." % low), ("I can label/draw %s." % low), ("I can answer past-paper questions on %s." % low)] if lang == "en"
                      else [("Ninaweza kufafanua %s bila madokezo." % low), ("Ninaweza kuchora/kuweka lebo %s." % low), ("Ninaweza kujibu maswali ya mitihani kuhusu %s." % low)])
    return d
'''
anchor = "BUILDERS = {"
if "build_scheme" not in vs:
    vs = vs.replace(anchor, NEW_BUILDERS.strip() + "\n\n\n" + anchor, 1)
    vs = vs.replace('BUILDERS = {"lesson_plan": build_lesson,',
                    'BUILDERS = {"lesson_plan": build_lesson, "scheme_of_work": build_scheme, "revision_notes": build_revision,', 1)
    vp.write_text(vs, encoding="utf-8")
tp = base / "templates/teacher_studio/studio.html"
html = tp.read_text(encoding="utf-8")
if 'value="scheme_of_work"' not in html:
    html = html.replace('<option value="activity">Learning Activity</option>',
                        '<option value="activity">Learning Activity</option><option value="scheme_of_work">Scheme of Work</option><option value="revision_notes">Revision Notes</option>', 1)
EXTRA = r'''
<script>
(function(){
  window.TYPE_LABEL = window.TYPE_LABEL || {};
  window.TYPE_LABEL.scheme_of_work = "Scheme of work";
  window.TYPE_LABEL.revision_notes = "Revision notes";
  var add = {en:{weeks:"Teaching weeks",coverage:"Coverage",key_terms:"Key terms",summary:"Summary",key_points:"Key points",worked:"Worked example",examq:"Exam practice",mnemonic:"Memory aid",checklist:"Revision checklist",lessons:"lessons"},
             sw:{weeks:"Wiki za mafundisho",coverage:"Funiko",key_terms:"Istilahi muhimu",summary:"Muhtasari",key_points:"Vipengele muhimu",worked:"Mfano uliofanywa",examq:"Mazoezi ya mtihani",mnemonic:"Kikumbusho",checklist:"Orodha ya marejeo",lessons:"masomo"}};
  for (var k in add.en){ window.I18N.en[k]=add.en[k]; window.I18N.sw[k]=add.sw[k]; }
  function hdr(d,b,L,sub){return header(d,b,L,sub);}
  function renderScheme(d,b,L){
    var wk=(d.weeks||[]).map(function(w){
      return '<div class="qcard"><div class="flex flex-wrap justify-between items-center gap-2 mb-2"><span class="chip" style="background:var(--indigo);color:#fff">Week '+w.week+'</span><span class="chip">'+w.lessons+' '+L.lessons+'</span></div>'
        +'<h3 class="font-bold mb-2" style="color:var(--indigo)">'+esc(w.subtopic)+'</h3>'
        +'<p class="text-xs font-bold mb-1" style="color:var(--mut)">'+L.out+'</p><ul style="margin:0 0 .5rem 1.1rem;font-size:.85rem">'+w.objectives.map(function(o){return '<li>'+esc(o)+'</li>';}).join("")+'</ul>'
        +'<p class="text-xs font-bold mb-1" style="color:var(--mut)">'+L.flow+'</p><ul style="margin:0 0 .5rem 1.1rem;font-size:.85rem">'+w.activities.map(function(a){return '<li>'+esc(a)+'</li>';}).join("")+'</ul>'
        +'<p class="text-xs" style="color:var(--mut)"><b>'+L.ass+':</b> '+esc(w.assessment)+'</p></div>';
    }).join("");
    return hdr(d,b,L,"Scheme of Work")+'<div class="stat mb-4" style="display:inline-block"><p>'+L.coverage+'</p><p style="font-size:.85rem">'+esc(d.coverage)+'</p></div><div class="grid md:grid-cols-2 gap-4">'+wk+'</div>'
      +'<div style="background:#FFFBEB;border-left:4px solid var(--amber);padding:1rem;margin-top:1rem"><strong style="color:#92400E">'+L.notes+':</strong> <span style="color:#92400E">'+esc(d.notes)+'</span></div>';
  }
  function renderRevision(d,b,L){
    var kt=(d.key_terms||[]).map(function(t){return '<span class="wb">'+esc(t)+'</span>';}).join("");
    var kp=(d.key_points||[]).map(function(p,i){return '<div class="oc"><b>'+(i+1)+'</b><span>'+esc(p)+'</span></div>';}).join("");
    var eq=(d.exam_questions||[]).map(function(q,i){return '<div class="qcard"><p class="font-medium">'+esc(q.q)+'</p><div class="answer"><strong>'+L.ans+':</strong> '+esc(q.a)+'</div></div>';}).join("");
    var ck=(d.checklist||[]).map(function(c){return '<div class="check"><span>'+esc(c)+'</span></div>';}).join("");
    return hdr(d,b,L,"Revision Notes")+'<h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.key_terms+'</h3><div class="mb-4">'+kt+'</div>'
      +'<h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.summary+'</h3><p style="color:var(--mut);font-size:.9rem" class="mb-5">'+esc(d.summary)+'</p>'
      +'<h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.key_points+'</h3><div class="space-y-2 mb-6">'+kp+'</div>'
      +'<h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.worked+'</h3><div style="background:#EEF6FF;border:1px dashed #2563EB;border-radius:.6rem;padding:.8rem 1rem;font-size:.9rem;color:#1E40AF" class="mb-6">'+esc(d.worked_example)+'</div>'
      +'<h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.examq+'</h3>'+eq
      +'<div style="background:#EEF2FF;border-left:4px solid var(--indigo);padding:.9rem 1rem;margin:1rem 0"><strong style="color:var(--indigo)">'+L.mnemonic+':</strong> <span style="letter-spacing:.2em;font-weight:800">'+esc(d.mnemonic)+'</span></div>'
      +'<h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.checklist+'</h3>'+ck;
  }
  var orig = window.renderAny;
  window.renderAny = function(d,b){
    if (d && d.kind === "scheme_of_work") return renderScheme(d,b,window.I18N[d.language==="sw"?"sw":"en"]);
    if (d && d.kind === "revision_notes") return renderRevision(d,b,window.I18N[d.language==="sw"?"sw":"en"]);
    return orig(d,b);
  };
})();
</script>
'''
if "renderScheme" not in html:
    i = html.rfind("{% endblock %}")
    html = html[:i] + EXTRA + html[i:]
    tp.write_text(html, encoding="utf-8")
pdfp = base / "static/js/studio_pdf.js"
pdf = pdfp.read_text(encoding="utf-8")
act = '    } else if (kind === "activity") {'
if 'kind === "scheme_of_work"' not in pdf and act in pdf:
    ins = '''    } else if (kind === "scheme_of_work") {
      section(L.weeks || "Teaching weeks");
      (d.weeks || []).forEach(function (wk, i) { stepBlock(i + 1, "Week " + wk.wk_week || wk.week, wk.lessons + " lessons", (wk.objectives || []).join(" ")); });
      section(L.coverage || "Coverage"); para(d.coverage, { size: 9.5, color: MUT });
      toneBox(L.notes, d.notes, "warn");
    } else if (kind === "revision_notes") {
      section(L.key_terms || "Key terms"); para((d.key_terms || []).join("  ·  "), { size: 9.5, style: "bold", color: INDIGO, after: 5 });
      section(L.summary || "Summary"); para(d.summary, { size: 9.5, color: MUT });
      section(L.key_points || "Key points"); (d.key_points || []).forEach(function (k, i) { numbered(i + 1, k); });
      section(L.worked || "Worked example"); para(d.worked_example, { size: 9.5, color: MUT });
      section(L.examq || "Exam practice");
      (d.exam_questions || []).forEach(function (q, i) { para(q.q, { size: 10, style: "bold", after: 2 }); if (withAnswers) toneBox(L.ans, q.a, "ok"); });
      toneBox(L.mnemonic || "Memory aid", d.mnemonic, "ok");
    } else if (kind === "activity") {'''
    pdf = pdf.replace(act, ins, 1)
    pdfp.write_text(pdf, encoding="utf-8")
# ============ B. COMPANION PROGRESS PANEL (base layer) ============
bp = base / "templates/base.html"
bh = bp.read_text(encoding="utf-8")
PROG = r'''<!-- JF_PROGRESS -->
<script>
(function(){
  if (location.pathname.indexOf("/learn/") !== 0) return;
  function mount(){
    if (document.getElementById("progCard")) return;
    var host = document.querySelector("main") || document.querySelector(".max-w-7xl") || document.body;
    var card = document.createElement("div");
    card.id = "progCard";
    card.className = "jf-card no-print";
    card.style.cssText = "padding:1rem 1.2rem;margin-bottom:1.1rem;background:var(--card,#fff);border:1px solid var(--line,#E4E1D6);border-radius:1rem";
    host.parentNode.insertBefore(card, host.nextSibling ? host : null) ;
    (host.parentNode || document.body).insertBefore(card, host);
    fetch("/api/learn/progress/", {credentials: "same-origin"}).then(function(r){return r.json();}).then(function(p){
      var max = Math.max.apply(null, (p.days||[]).map(function(d){return d.count;}).concat([1]));
      var spark = (p.days||[]).map(function(d){return '<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:3px"><div style="width:100%;border-radius:4px 4px 0 0;background:linear-gradient(180deg,#10B981,#0b8457);height:'+Math.max(4,Math.round(40*d.count/max))+'px"></div><span style="font-size:.6rem;color:var(--mut,#64748B);font-weight:600">'+d.date+'</span></div>';}).join("");
      card.innerHTML = '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.6rem"><h3 style="font-family:Manrope,Inter,sans-serif;font-weight:800;color:var(--indigo,#1B1F4B);font-size:.95rem">My learning progress</h3></div>'
        + '<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:.6rem" class="md:grid-cols-4">'
        + '<div style="background:var(--soft,#F6F4EC);border:1px solid var(--line,#E4E1D6);border-radius:.7rem;padding:.6rem .8rem"><p style="font-size:.62rem;text-transform:uppercase;color:var(--mut,#64748B);font-weight:700">Sessions</p><p style="font-family:Manrope;font-weight:800;font-size:1.3rem;color:var(--indigo,#1B1F4B)">'+(p.sessions||0)+'</p></div>'
        + '<div style="background:var(--soft,#F6F4EC);border:1px solid var(--line,#E4E1D6);border-radius:.7rem;padding:.6rem .8rem"><p style="font-size:.62rem;text-transform:uppercase;color:var(--mut,#64748B);font-weight:700">Questions asked</p><p style="font-family:Manrope;font-weight:800;font-size:1.3rem;color:var(--indigo,#1B1F4B)">'+(p.messages||0)+'</p></div>'
        + '<div style="background:var(--soft,#F6F4EC);border:1px solid var(--line,#E4E1D6);border-radius:.7rem;padding:.6rem .8rem"><p style="font-size:.62rem;text-transform:uppercase;color:var(--mut,#64748B);font-weight:700">Sources consulted</p><p style="font-family:Manrope;font-weight:800;font-size:1.3rem;color:var(--indigo,#1B1F4B)">'+(p.sources||0)+'</p></div>'
        + '<div style="background:var(--soft,#F6F4EC);border:1px solid var(--line,#E4E1D6);border-radius:.7rem;padding:.6rem .8rem"><p style="font-size:.62rem;text-transform:uppercase;color:var(--mut,#64748B);font-weight:700">Active days</p><p style="font-family:Manrope;font-weight:800;font-size:1.3rem;color:var(--indigo,#1B1F4B)">'+(p.active_days||0)+'</p></div>'
        + '</div>'
        + '<div style="display:flex;align-items:flex-end;gap:5px;height:56px;margin-top:.8rem">'+spark+'</div>'
        + ((p.topics&&p.topics.length)?('<div style="margin-top:.7rem">'+p.topics.map(function(t){return '<span style="display:inline-block;background:#EEF0F6;border:1px solid var(--line,#E4E1D6);border-radius:9999px;padding:.2rem .6rem;font-size:.7rem;font-weight:600;margin:.1rem">'+t+'</span>';}).join("")+'</div>'):'');
    }).catch(function(){ card.remove(); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount); else mount();
})();
</script>
'''
if "JF_PROGRESS" not in bh:
    bh = bh.replace("</body>", PROG + "</body>", 1)
    bp.write_text(bh, encoding="utf-8")
# ============ D2. LIBRARY SEMANTIC SEARCH TOGGLE ============
lp = base / "templates/resources/library.html"
lh = lp.read_text(encoding="utf-8")
if 'id="searchMode"' not in lh:
    lh = lh.replace('<input name="q" value="{{ q }}" placeholder="Search title, topic, subject" class="md:col-span-2">',
                    '<div class="md:col-span-2 flex gap-2"><input name="q" id="libq" value="{{ q }}" placeholder="Search title, topic, subject" class="flex-1"><select id="searchMode" style="max-width:130px"><option value="keyword">Keyword</option><option value="semantic">Semantic</option></select></div>', 1)
    lh = lh.replace('<div class="grid md:grid-cols-2 xl:grid-cols-3 gap-5">', '<div id="libGrid" class="grid md:grid-cols-2 xl:grid-cols-3 gap-5">', 1)
    lh = lh.replace("{% endblock %}", '''<script>
(function(){
  var f = document.querySelector("#libGrid") ? document.querySelector("form") : null;
  if (!f) return;
  f.addEventListener("submit", function(e){
    var mode = document.getElementById("searchMode");
    if (!mode || mode.value !== "semantic") return;
    e.preventDefault();
    var q = document.getElementById("libq").value.trim();
    if (!q) return;
    fetch("/api/resources/semantic_search/?q=" + encodeURIComponent(q), {credentials:"same-origin"})
      .then(function(r){return r.json();}).then(function(j){
        var grid = document.getElementById("libGrid");
        grid.innerHTML = (j.results||[]).map(function(x){
          return '<div class="lb-card p-5"><div class="flex items-start justify-between gap-2 mb-2"><h3 class="font-bold" style="color:var(--indigo)">'+x.title+'</h3><span class="badge bA">'+x.score+'</span></div>'
            + '<div class="flex flex-wrap gap-1.5 mb-2">'+(x.subject?'<span class="chip">'+x.subject+'</span>':'')+(x.grade?'<span class="chip">'+x.grade+'</span>':'')+'</div>'
            + '<p style="font-size:.8rem;color:var(--mut)">'+x.chunk+'…</p></div>';
        }).join("") || '<p style="color:var(--mut)">No semantic matches. Run <code>python manage.py build_embeddings</code> first.</p>';
      });
  });
})();
</script>
{% endblock %}''', 1)
    lp.write_text(lh, encoding="utf-8")
w("apps/resources/management/commands/build_embeddings.py", '''from django.core.management.base import BaseCommand
from apps.learning.semantic import encode
from apps.resources.models import DocumentChunk
class Command(BaseCommand):
    help = "Populate DocumentChunk.embedding vectors for semantic search."
    def handle(self, *args, **o):
        n = 0
        for c in DocumentChunk.objects.all():
            if not c.embedding:
                c.embedding = encode(c.chunk_text or "")
                c.save(update_fields=["embedding"])
                n += 1
        self.stdout.write(self.style.SUCCESS("Embedded %d chunks." % n))
''')
(base / "apps/resources/management/__init__.py").touch(exist_ok=True)
(base / "apps/resources/management/commands/__init__.py").touch(exist_ok=True)
print("FINAL BUNDLE INSTALLED")
