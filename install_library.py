from pathlib import Path
import re
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
VIEWS = '''from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from apps.institutions.models import Membership
from apps.resources.models import DocumentChunk, LearningResource
@login_required(login_url="/accounts/login/")
def library_page(request):
    m = Membership.objects.filter(user=request.user, is_active=True).first()
    fields = {f.name for f in LearningResource._meta.fields}
    base_qs = LearningResource.objects.filter(institution=m.institution) if m else LearningResource.objects.none()
    qs = base_qs
    q = request.GET.get("q", "").strip()
    cur = request.GET.get("curriculum", "").strip()
    grade = request.GET.get("grade", "").strip()
    subj = request.GET.get("subject", "").strip()
    tier = request.GET.get("tier", "").strip()
    if q:
        cond = Q(title__icontains=q)
        if "topic" in fields:
            cond |= Q(topic__icontains=q)
        if "subject" in fields:
            cond |= Q(subject__icontains=q)
        qs = qs.filter(cond)
    if cur and "curriculum" in fields:
        qs = qs.filter(curriculum=cur)
    if grade and "grade_level" in fields:
        qs = qs.filter(grade_level=grade)
    if subj and "subject" in fields:
        qs = qs.filter(subject=subj)
    if tier and "provenance_tier" in fields:
        qs = qs.filter(provenance_tier=tier)
    order = "-created_at" if "created_at" in fields else "-id"
    rows = []
    for r in qs.order_by(order)[:200]:
        file_url = ""
        try:
            if getattr(r, "file", None):
                file_url = r.file.url
        except Exception:
            file_url = ""
        rows.append({
            "title": r.title,
            "subject": getattr(r, "subject", ""),
            "grade": getattr(r, "grade_level", ""),
            "curriculum": getattr(r, "curriculum", ""),
            "topic": getattr(r, "topic", ""),
            "tier": getattr(r, "provenance_tier", "A"),
            "license": getattr(r, "license", ""),
            "attribution": getattr(r, "attribution", ""),
            "source_url": getattr(r, "source_url", ""),
            "chunks": DocumentChunk.objects.filter(resource=r).count(),
            "file_url": file_url,
        })
    def distinct(field):
        if not m or field not in fields:
            return []
        return sorted({v for v in base_qs.values_list(field, flat=True) if v})
    counts = {"A": 0, "B": 0, "C": 0}
    for row in rows:
        counts[row["tier"]] = counts.get(row["tier"], 0) + 1
    return render(request, "resources/library.html", {
        "rows": rows, "q": q, "counts": counts,
        "curricula": distinct("curriculum"), "grades": distinct("grade_level"), "subjects": distinct("subject"),
        "sel": {"curriculum": cur, "grade": grade, "subject": subj, "tier": tier},
        "institution": m.institution if m else None,
    })
'''
(base / "apps/resources/library_views.py").write_text(VIEWS, encoding="utf-8")
TPL = '''{% extends "base.html" %}
{% block title %}My Library — JIFUNZE AI{% endblock %}
{% block content %}
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<style>
  :root{--indigo:#1B1F4B;--green:#10B981;--amber:#F59E0B;--bg:#FDFCF8;--card:#fff;--ink:#0F172A;--mut:#64748B;--line:#E4E1D6;--soft:#F6F4EC;}
  .lb{font-family:Inter,sans-serif;color:var(--ink);}
  .lb h1,.lb h2,.lb h3{font-family:Manrope,sans-serif;}
  .lb-card{background:var(--card);border:1px solid var(--line);border-radius:1rem;box-shadow:0 6px 18px -8px rgba(27,31,75,.14);}
  .lb input,.lb select{border:1px solid var(--line);border-radius:.6rem;padding:.55rem .7rem;background:#fff;font-size:.875rem;}
  .lb input:focus,.lb select:focus{outline:none;border-color:var(--indigo);box-shadow:0 0 0 3px rgba(27,31,75,.14);}
  .badge{font-size:.65rem;font-weight:800;letter-spacing:.05em;padding:.2rem .55rem;border-radius:9999px;}
  .bA{background:#DCFCE7;color:#166534;} .bB{background:#FEF3C7;color:#92400E;} .bC{background:#E2E8F0;color:#334155;}
  .chip{font-size:.68rem;font-weight:700;padding:.18rem .5rem;border-radius:9999px;background:#EEF0F6;color:#3B4270;}
  .lb-btn{display:inline-flex;align-items:center;gap:.4rem;font-size:.8rem;font-weight:600;border-radius:.55rem;padding:.45rem .8rem;border:1px solid var(--line);background:#fff;color:var(--ink);text-decoration:none;transition:.15s;}
  .lb-btn:hover{background:var(--soft);}
  .lb-btn.primary{background:var(--indigo);color:#fff;border-color:var(--indigo);}
  .lb-btn.primary:hover{background:#2A3070;}
</style>
<div class="lb max-w-7xl mx-auto px-4 py-8">
  <div class="flex flex-wrap items-end justify-between gap-4 mb-6">
    <div>
      <h1 class="text-3xl font-extrabold" style="color:var(--indigo)">My Library</h1>
      <p class="mt-1" style="color:var(--mut)">School-owned resources with provenance, licence and attribution{% if institution %} · {{ institution.name }}{% endif %}</p>
    </div>
    <div class="flex gap-2">
      <span class="badge bA">Ingested {{ counts.A }}</span>
      <span class="badge bB">Link-out {{ counts.B }}</span>
      <span class="badge bC">Private {{ counts.C }}</span>
    </div>
  </div>
  <form method="get" class="lb-card p-4 mb-6 grid md:grid-cols-6 gap-3">
    <input name="q" value="{{ q }}" placeholder="Search title, topic, subject" class="md:col-span-2">
    <select name="curriculum"><option value="">All curricula</option>{% for c in curricula %}<option {% if sel.curriculum == c %}selected{% endif %}>{{ c }}</option>{% endfor %}</select>
    <select name="grade"><option value="">All grades</option>{% for g in grades %}<option {% if sel.grade == g %}selected{% endif %}>{{ g }}</option>{% endfor %}</select>
    <select name="subject"><option value="">All subjects</option>{% for s in subjects %}<option {% if sel.subject == s %}selected{% endif %}>{{ s }}</option>{% endfor %}</select>
    <div class="flex gap-2">
      <select name="tier" class="flex-1"><option value="">All tiers</option><option value="A" {% if sel.tier == "A" %}selected{% endif %}>A · Ingested</option><option value="B" {% if sel.tier == "B" %}selected{% endif %}>B · Link-out</option><option value="C" {% if sel.tier == "C" %}selected{% endif %}>C · Private</option></select>
      <button class="lb-btn primary" type="submit">Filter</button>
    </div>
  </form>
  {% if rows %}
  <div class="grid md:grid-cols-2 xl:grid-cols-3 gap-5">
    {% for r in rows %}
    <div class="lb-card p-5 flex flex-col">
      <div class="flex items-start justify-between gap-3 mb-2">
        <h3 class="font-bold text-base leading-snug" style="color:var(--indigo)">{{ r.title }}</h3>
        <span class="badge b{{ r.tier }}">{% if r.tier == "A" %}INGESTED{% elif r.tier == "B" %}LINK-OUT{% else %}PRIVATE{% endif %}</span>
      </div>
      <div class="flex flex-wrap gap-1.5 mb-3">
        {% if r.curriculum %}<span class="chip">{{ r.curriculum }}</span>{% endif %}
        {% if r.grade %}<span class="chip">{{ r.grade }}</span>{% endif %}
        {% if r.subject %}<span class="chip">{{ r.subject }}</span>{% endif %}
        {% if r.topic %}<span class="chip">{{ r.topic }}</span>{% endif %}
      </div>
      <p class="text-xs mb-1" style="color:var(--mut)"><strong>Chunks indexed:</strong> {{ r.chunks }}</p>
      {% if r.license %}<p class="text-xs mb-1" style="color:var(--mut)"><strong>Licence:</strong> {{ r.license }}</p>{% endif %}
      {% if r.attribution %}<p class="text-xs mb-3" style="color:var(--mut)"><strong>Attribution:</strong> {{ r.attribution }}</p>{% endif %}
      <div class="mt-auto flex flex-wrap gap-2 pt-2">
        {% if r.tier == "B" and r.source_url %}
          <a class="lb-btn primary" href="{{ r.source_url }}" target="_blank" rel="noopener">Open official source</a>
        {% elif r.file_url %}
          <a class="lb-btn" href="{{ r.file_url }}" target="_blank" rel="noopener">Open file</a>
        {% endif %}
        {% if r.tier == "C" %}<span class="text-xs self-center" style="color:var(--mut)">Reference only — not in learner search</span>{% endif %}
      </div>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <div class="lb-card p-16 text-center" style="border:2px dashed var(--line);color:var(--mut)">
    No resources match. Import a pack or upload materials to populate your library.
  </div>
  {% endif %}
</div>
{% endblock %}'''
(base / "templates/resources/library.html").write_text(TPL, encoding="utf-8")
up = base / "config/urls.py"
content = up.read_text(encoding="utf-8")
if "library_views" not in content:
    content = "from apps.resources import library_views\n" + content
new = re.sub(r'path\("library/",\s*[^,]+,\s*name="library"\)',
             'path("library/", library_views.library_page, name="library")', content)
if new == content:
    print("WARNING: library URL pattern not found - check config/urls.py")
else:
    up.write_text(new, encoding="utf-8")
    print("LIBRARY WIRED")
print("LIBRARY INSTALLED")
