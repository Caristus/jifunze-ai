import re, socket
from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
def w(rel, text):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
# ============ BLOCKER 2: GitHub-ready files ============
w(".gitignore", """# Python
__pycache__/
*.py[cod]
*.egg-info/
venv/
env/
.env
*.env
# Django
db.sqlite3
db.sqlite3-journal
staticfiles/
media/
!media/.gitkeep
# IDE / OS
.vscode/
.idea/
.DS_Store
Thumbs.db
# Test / coverage
.pytest_cache/
.coverage
htmlcov/
# Local helpers
fix_*.py
install_*.py
repair_*.py
""")
w("media/.gitkeep", "")
w("README.md", """# JIFUNZE AI
**Intelligence for everyone. Knowledge without boundaries.**
An open-source, community-governed AI learning infrastructure for African schools — built with Django, provider-independent AI, retrieval-augmented generation and school-level data sovereignty.
![tests](https://github.com/USERNAME/jifunze-ai/workflows/tests/badge.svg)
![license](https://img.shields.io/badge/license-Apache--2.0-blue)
## Three modules
- **Learning Companion** — level-aware AI tutor grounded in your school's approved materials, with source citations and open-knowledge fallback.
- **Teacher Studio** — lesson plans, schemes of work, quizzes (10 question types, auto-marking), worksheets, marking guides, activities and revision notes; AI refine actions; branded PDF export.
- **Data Sovereignty Centre** — consent records, data export/deletion workflows, AI provider transparency, retention policy and a full audit trail.
## Quick start
```bash
python -m venv venv && source venv/bin/activate   # or venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo          # optional demo data
python manage.py runserver
def handle(self, *args, **o):
    inst, _ = Institution.objects.get_or_create(name="Jifunze Test School", defaults={"country": "Kenya"})
    if not hasattr(inst, "retention_days"):
        pass
    admin, _ = User.objects.get_or_create(username="admin", defaults={"role": "platform_admin"})
    admin.set_password("admin12345!"); admin.save()
    caristus, _ = User.objects.get_or_create(username="Caristus_Mugendi", defaults={"role": "school_admin"})
    caristus.set_password("admin12345!"); caristus.save()
    teacher, _ = User.objects.get_or_create(username="teacher.demo", defaults={"role": "teacher"})
    teacher.set_password("teach12345!"); teacher.save()
    learner, _ = User.objects.get_or_create(username="learner.demo", defaults={"role": "learner"})
    learner.set_password("learn12345!"); learner.save()
    for u, r in ((admin, "platform_admin"), (caristus, "school_admin"), (teacher, "teacher"), (learner, "learner")):
        Membership.objects.get_or_create(user=u, institution=inst, defaults={"role": r, "is_active": True})
    lr_f, dc_f = fields(LearningResource), fields(DocumentChunk)
    made_res = 0
    chunks_by_title = {}
    for title, subj, grade, curr, text in RESOURCES:
        kwargs = {"institution": inst, "title": title, "status": "ready", "uploaded_by": teacher}
        for f, v in (("subject", subj), ("grade_level", grade), ("curriculum", curr), ("topic", title.split(" - ")[0]),
                     ("provenance_tier", "A"), ("license", "CC0 (demo original)"), ("source_url", ""),
                     ("attribution", "JIFUNZE AI demo content")):
            if f in lr_f:
                kwargs[f] = v
        res, created = LearningResource.objects.update_or_create(institution=inst, title=title,
                                                                 defaults={k: v for k, v in kwargs.items() if k not in ("institution", "title")})
        if created:
            made_res += 1
        DocumentChunk.objects.filter(resource=res).delete()
        halves = [text[:len(text)//2], text[len(text)//2:]]
        cl = []
        for i, half in enumerate(halves):
            ck = {"resource": res, "chunk_index": i, "chunk_text": half.strip()}
            cl.append(DocumentChunk.objects.create(**{k: v for k, v in ck.items() if k in dc_f or k == "resource"}))
        chunks_by_title[title] = cl
    made_art = 0
    specs = [("lesson_plan", "Photosynthesis", "Form 2", "CBC/CBE"),
             ("quiz", "Atomic Structure", "Form 2", "CBC/CBE"),
             ("worksheet", "Fractions", "Grade 8", "CBC/CBE"),
             ("marking_guide", "Photosynthesis", "Form 2", "CBC/CBE"),
             ("scheme_of_work", "Forces and Motion", "Form 1", "8-4-4")]
    for kind, topic, grade, curr in specs:
        params = {"artifact_type": kind, "topic": topic, "grade_level": grade, "curriculum": curr,
                  "language": "en", "duration": 50, "count": 8, "mix": "balanced", "difficulty": "Standard"}
        content = json.dumps(BUILDERS[kind](params), indent=2)
        kwargs = {"institution": inst, "created_by": teacher, "artifact_type": kind, "topic": topic, "content": content}
        ex = {f.name for f in __import__("apps.teacher_studio.models", fromlist=["TeachingArtifact"]).TeachingArtifact._meta.fields}
        for f in ("grade_level", "curriculum"):
            if f in ex:
                kwargs[f] = grade if f == "grade_level" else curr
        from apps.teacher_studio.models import TeachingArtifact
        if not TeachingArtifact.objects.filter(institution=inst, topic=topic, artifact_type=kind).exists():
            TeachingArtifact.objects.create(**kwargs)
            made_art += 1
    cf, mf, sf = fields(Conversation), fields(Message), fields(MessageSource)
    made_conv = 0
    for title, subj, answer in CONVERSATIONS:
        if Conversation.objects.filter(institution=inst, title=title).exists():
            continue
        ck = {"institution": inst, "title": title}
        if "user" in cf:
            ck["user"] = learner
        if "subject" in cf:
            ck["subject"] = subj
        conv = Conversation.objects.create(**ck)
        mk = {"conversation": conv, "content": title}
        if "role" in mf:
            mk["role"] = "user"
        Message.objects.create(**mk)
        ak = {"conversation": conv, "content": answer}
        if "role" in mf:
            ak["role"] = "assistant"
        am = Message.objects.create(**ak)
        match = [t for t in chunks_by_title if t.lower().split(" ")[0] in title.lower() or title.lower().split(" ")[-1] in t.lower()]
        src_title = match[0] if match else RESOURCES[0][0]
        if "message" in sf:
            sk = {"message": am}
            if "resource" in sf:
                sk["resource"] = chunks_by_title[src_title][0].resource
            if "chunk" in sf:
                sk["chunk"] = chunks_by_title[src_title][0]
            MessageSource.objects.create(**sk)
        made_conv += 1
    try:
        from apps.governance.models import ConsentRecord, DataRequest
        crf = fields(ConsentRecord)
        ck2 = {"institution": inst, "user": learner}
        for f in ("policy_version", "version"):
            if f in crf:
                ck2[f] = "v1.0"
        for f in ("granted", "consent", "accepted"):
            if f in crf:
                ck2[f] = True
        if not ConsentRecord.objects.filter(institution=inst, user=learner).exists():
            ConsentRecord.objects.create(**{k: v for k, v in ck2.items() if k in crf})
        drf = fields(DataRequest)
        dk = {"institution": inst, "user": learner}
        for f in ("request_type", "type"):
            if f in drf:
                dk[f] = "export"
        for f in ("status",):
            if f in drf:
                dk[f] = "pending"
        if not DataRequest.objects.filter(institution=inst, user=learner).exists():
            DataRequest.objects.create(**{k: v for k, v in dk.items() if k in drf})
    except Exception as e:
        self.stdout.write("governance seed skipped: %s" % e)
    try:
        ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip.connect(("8.8.8.8", 80)); lan = ip.getsockname()[0]; ip.close()
    except Exception:
        lan = "127.0.0.1"
    self.stdout.write(self.style.SUCCESS(
        "DEMO DATA READY  resources+=%d artifacts+=%d conversations+=%d" % (made_res, made_art, made_conv)))
    self.stdout.write("Logins: admin/admin12345!  Caristus_Mugendi/admin12345!  teacher.demo/teach12345!  learner.demo/learn12345!")
    self.stdout.write("Mobile test: python manage.py runserver 0.0.0.0:8000  then open http://%s:8000 on your phone" % lan)
BLOCKER 1: demo data seeder ============
sd = base / "apps/accounts/management/commands"
sd.mkdir(parents=True, exist_ok=True)
(base / "apps/accounts/management/init.py").touch(exist_ok=True)
(sd / "init.py").touch(exist_ok=True)
w("apps/accounts/management/commands/seed_demo.py", '''import json
import os
import socket
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.institutions.models import Institution, Membership
from apps.learning.models import Conversation, Message, MessageSource
from apps.resources.models import DocumentChunk, LearningResource
from apps.teacher_studio.views import BUILDERS
RESOURCES = [
("Photosynthesis - Form 2 Biology Notes", "Biology", "Form 2", "CBC/CBE",
"Photosynthesis is the process by which green plants convert light energy into chemical energy stored in glucose. It takes place in chloroplasts, where the pigment chlorophyll absorbs mainly red and blue light. The overall equation is 6CO2 + 6H2O + light -> C6H12O6 + 6O2. The light-dependent reactions split water, releasing oxygen and producing ATP and NADPH. The Calvin cycle then uses these products to fix carbon dioxide into glucose. Factors affecting the rate include light intensity, carbon dioxide concentration and temperature."),
("Atomic Structure - Form 2 Chemistry Notes", "Chemistry", "Form 2", "CBC/CBE",
"An atom is the smallest particle of an element that retains its chemical properties. It consists of a dense central nucleus containing protons and neutrons, surrounded by electrons arranged in energy levels or shells. Protons carry a positive charge, electrons a negative charge and neutrons are neutral. The atomic number equals the number of protons and defines the element, while the mass number is the total of protons and neutrons. Isotopes are atoms of the same element with different numbers of neutrons."),
("Fractions and Operations - Grade 8 Mathematics", "Mathematics", "Grade 8", "CBC/CBE",
"A fraction represents a part of a whole and is written as a numerator over a denominator. Equivalent fractions have the same value even though they look different, for example 1/2 and 2/4. To add or subtract fractions, first express them with a common denominator. To multiply fractions, multiply the numerators and multiply the denominators. To divide, multiply by the reciprocal of the second fraction. Always simplify your final answer by dividing top and bottom by their greatest common factor."),
("Causes of the First World War - Form 3 History", "History", "Form 3", "8-4-4",
"The immediate cause of the First World War was the assassination of Archduke Franz Ferdinand of Austria-Hungary at Sarajevo in June 1914. Long-term causes are summarised as militarism, alliances, imperialism and nationalism. Europe was divided into two armed camps: the Triple Entente of Britain, France and Russia, and the Triple Alliance of Germany, Austria-Hungary and Italy. The war ended in 1918 and the Treaty of Versailles of 1919 imposed harsh terms on Germany."),
("Forces and Newton's Laws - Form 1 Physics", "Physics", "Form 1", "8-4-4",
"A force is a push or a pull that can change the shape, speed or direction of motion of a body. The SI unit of force is the newton. Newton's first law states that a body remains at rest or in uniform motion unless acted on by an external force. Newton's second law gives force as mass times acceleration, F = ma. Newton's third law states that every action has an equal and opposite reaction. Friction opposes relative motion between surfaces in contact."),
]
CONVERSATIONS = [
("Explain photosynthesis", "Biology",
"Photosynthesis is how green plants turn light energy into chemical energy (glucose). It happens in chloroplasts, where chlorophyll absorbs mainly red and blue light. The overall equation is 6CO2 + 6H2O + light -> C6H12O6 + 6O2. The light-dependent reactions split water and make ATP and NADPH; the Calvin cycle then fixes CO2 into glucose. (Biology · CBC/CBE · Form 2)"),
("What is an atom?", "Chemistry",
"An atom is the smallest unit of an element that keeps its chemical properties. It has a dense nucleus of protons (positive) and neutrons (neutral), with negatively charged electrons orbiting in shells. The number of protons (the atomic number) defines the element. (Chemistry · CBC/CBE · Form 2)"),
("How do I add 1/2 and 1/4?", "Mathematics",
"To add 1/2 and 1/4, first find a common denominator, which is 4. Convert 1/2 to 2/4, then add the numerators: 2/4 + 1/4 = 3/4. So the answer is 3/4. (Mathematics · CBC/CBE · Grade 8)"),
]
def fields(model):
return {f.name for f in model._meta.fields}
class Command(BaseCommand):
help = "Populate the platform with realistic demo data for recordings and pilots."
def handle(self, *args, **o):
    inst, _ = Institution.objects.get_or_create(name="Jifunze Test School", defaults={"country": "Kenya"})
    if not hasattr(inst, "retention_days"):
        pass
    admin, _ = User.objects.get_or_create(username="admin", defaults={"role": "platform_admin"})
    admin.set_password("admin12345!"); admin.save()
    caristus, _ = User.objects.get_or_create(username="Caristus_Mugendi", defaults={"role": "school_admin"})
    caristus.set_password("admin12345!"); caristus.save()
    teacher, _ = User.objects.get_or_create(username="teacher.demo", defaults={"role": "teacher"})
    teacher.set_password("teach12345!"); teacher.save()
    learner, _ = User.objects.get_or_create(username="learner.demo", defaults={"role": "learner"})
    learner.set_password("learn12345!"); learner.save()
    for u, r in ((admin, "platform_admin"), (caristus, "school_admin"), (teacher, "teacher"), (learner, "learner")):
        Membership.objects.get_or_create(user=u, institution=inst, defaults={"role": r, "is_active": True})
    lr_f, dc_f = fields(LearningResource), fields(DocumentChunk)
    made_res = 0
    chunks_by_title = {}
    for title, subj, grade, curr, text in RESOURCES:
        kwargs = {"institution": inst, "title": title, "status": "ready", "uploaded_by": teacher}
        for f, v in (("subject", subj), ("grade_level", grade), ("curriculum", curr), ("topic", title.split(" - ")[0]),
                     ("provenance_tier", "A"), ("license", "CC0 (demo original)"), ("source_url", ""),
                     ("attribution", "JIFUNZE AI demo content")):
            if f in lr_f:
                kwargs[f] = v
        res, created = LearningResource.objects.update_or_create(institution=inst, title=title,
                                                                 defaults={k: v for k, v in kwargs.items() if k not in ("institution", "title")})
        if created:
            made_res += 1
        DocumentChunk.objects.filter(resource=res).delete()
        halves = [text[:len(text)//2], text[len(text)//2:]]
        cl = []
        for i, half in enumerate(halves):
            ck = {"resource": res, "chunk_index": i, "chunk_text": half.strip()}
            cl.append(DocumentChunk.objects.create(**{k: v for k, v in ck.items() if k in dc_f or k == "resource"}))
        chunks_by_title[title] = cl
    made_art = 0
    specs = [("lesson_plan", "Photosynthesis", "Form 2", "CBC/CBE"),
             ("quiz", "Atomic Structure", "Form 2", "CBC/CBE"),
             ("worksheet", "Fractions", "Grade 8", "CBC/CBE"),
             ("marking_guide", "Photosynthesis", "Form 2", "CBC/CBE"),
             ("scheme_of_work", "Forces and Motion", "Form 1", "8-4-4")]
    for kind, topic, grade, curr in specs:
        params = {"artifact_type": kind, "topic": topic, "grade_level": grade, "curriculum": curr,
                  "language": "en", "duration": 50, "count": 8, "mix": "balanced", "difficulty": "Standard"}
        content = json.dumps(BUILDERS[kind](params), indent=2)
        kwargs = {"institution": inst, "created_by": teacher, "artifact_type": kind, "topic": topic, "content": content}
        ex = {f.name for f in __import__("apps.teacher_studio.models", fromlist=["TeachingArtifact"]).TeachingArtifact._meta.fields}
        for f in ("grade_level", "curriculum"):
            if f in ex:
                kwargs[f] = grade if f == "grade_level" else curr
        from apps.teacher_studio.models import TeachingArtifact
        if not TeachingArtifact.objects.filter(institution=inst, topic=topic, artifact_type=kind).exists():
            TeachingArtifact.objects.create(**kwargs)
            made_art += 1
    cf, mf, sf = fields(Conversation), fields(Message), fields(MessageSource)
    made_conv = 0
    for title, subj, answer in CONVERSATIONS:
        if Conversation.objects.filter(institution=inst, title=title).exists():
            continue
        ck = {"institution": inst, "title": title}
        if "user" in cf:
            ck["user"] = learner
        if "subject" in cf:
            ck["subject"] = subj
        conv = Conversation.objects.create(**ck)
        mk = {"conversation": conv, "content": title}
        if "role" in mf:
            mk["role"] = "user"
        Message.objects.create(**mk)
        ak = {"conversation": conv, "content": answer}
        if "role" in mf:
            ak["role"] = "assistant"
        am = Message.objects.create(**ak)
        match = [t for t in chunks_by_title if t.lower().split(" ")[0] in title.lower() or title.lower().split(" ")[-1] in t.lower()]
        src_title = match[0] if match else RESOURCES[0][0]
        if "message" in sf:
            sk = {"message": am}
            if "resource" in sf:
                sk["resource"] = chunks_by_title[src_title][0].resource
            if "chunk" in sf:
                sk["chunk"] = chunks_by_title[src_title][0]
            MessageSource.objects.create(**sk)
        made_conv += 1
    try:
        from apps.governance.models import ConsentRecord, DataRequest
        crf = fields(ConsentRecord)
        ck2 = {"institution": inst, "user": learner}
        for f in ("policy_version", "version"):
            if f in crf:
                ck2[f] = "v1.0"
        for f in ("granted", "consent", "accepted"):
            if f in crf:
                ck2[f] = True
        if not ConsentRecord.objects.filter(institution=inst, user=learner).exists():
            ConsentRecord.objects.create(**{k: v for k, v in ck2.items() if k in crf})
        drf = fields(DataRequest)
        dk = {"institution": inst, "user": learner}
        for f in ("request_type", "type"):
            if f in drf:
                dk[f] = "export"
        for f in ("status",):
            if f in drf:
                dk[f] = "pending"
        if not DataRequest.objects.filter(institution=inst, user=learner).exists():
            DataRequest.objects.create(**{k: v for k, v in dk.items() if k in drf})
    except Exception as e:
        self.stdout.write("governance seed skipped: %s" % e)
    try:
        ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip.connect(("8.8.8.8", 80)); lan = ip.getsockname()[0]; ip.close()
    except Exception:
        lan = "127.0.0.1"
    self.stdout.write(self.style.SUCCESS(
        "DEMO DATA READY  resources+=%d artifacts+=%d conversations+=%d" % (made_res, made_art, made_conv)))
    self.stdout.write("Logins: admin/admin12345!  Caristus_Mugendi/admin12345!  teacher.demo/teach12345!  learner.demo/learn12345!")
    self.stdout.write("Mobile test: python manage.py runserver 0.0.0.0:8000  then open http://%s:8000 on your phone" % lan)
''')
============ BLOCKER 3: Bulk Onboard ============
w("apps/accounts/bulk_views.py", '''import csv
import io
import random
import string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from apps.accounts.models import User
from apps.institutions.models import Institution, Membership
def _parse(text):
rows = []
reader = csv.reader(io.StringIO(text or ""))
for r in reader:
r = [c.strip() for c in r if c.strip()]
if not r:
continue
if r[0].lower() in ("username", "name"):
continue
username = r[0]
role = r[1] if len(r) > 1 else "learner"
grade = r[2] if len(r) > 2 else ""
rows.append((username, role, grade))
return rows
@login_required(login_url="/accounts/login/")
def onboard_page(request):
results = request.session.pop("onboard_results", None)
return render(request, "accounts/onboard.html", {"results": results})
@login_required(login_url="/accounts/login/")
def onboard_run(request):
if request.method != "POST":
return HttpResponse(status=405)
m = Membership.objects.filter(user=request.user, is_active=True).first()
inst = m.institution if m else Institution.objects.first()
text = request.POST.get("csv", "")
if request.FILES.get("file"):
text = request.FILES["file"].read().decode("utf-8-sig", errors="ignore")
rows = _parse(text)
results = []
for username, role, grade in rows:
password = "Jif!" + "".join(random.choices(string.digits, k=4))
u, created = User.objects.get_or_create(username=username, defaults={"role": role})
if created:
u.set_password(password)
u.save()
else:
password = "(existing user)"
Membership.objects.get_or_create(user=u, institution=inst, defaults={"role": role, "is_active": True})
results.append({"username": username, "role": role, "grade": grade, "password": password, "created": created})
request.session["onboard_results"] = results
request.session["onboard_inst"] = str(inst.id) if inst else ""
return redirect_back(request)
def redirect_back(request):
from django.shortcuts import redirect
return redirect("/onboard/")
@login_required(login_url="/accounts/login/")
def onboard_csv(request):
results = request.session.get("onboard_results") or []
resp = HttpResponse(content_type="text/csv")
resp["Content-Disposition"] = 'attachment; filename="jifunze_credentials.csv"'
writer = csv.writer(resp)
writer.writerow(["username", "role", "grade", "temporary_password"])
for r in results:
writer.writerow([r["username"], r["role"], r["grade"], r["password"]])
return resp
''')
w("templates/accounts/onboard.html", '''{% extends "base.html" %}
{% block title %}Bulk Onboard — JIFUNZE AI{% endblock %}
{% block content %}
<style>
.ob{font-family:Inter,sans-serif;color:#0F172A;}
.ob-card{background:#fff;border:1px solid #E4E1D6;border-radius:1rem;box-shadow:0 6px 18px -8px rgba(27,31,75,.14);padding:1.4rem;}
.ob textarea{width:100%;min-height:160px;border:1px solid #E4E1D6;border-radius:.7rem;padding:.8rem;font-family:monospace;font-size:.85rem;}
.ob table{width:100%;border-collapse:collapse;font-size:.82rem;margin-top:1rem;}
.ob th,.ob td{border:1px solid #E4E1D6;padding:.5rem .6rem;text-align:left;}
.ob th{background:#1B1F4B;color:#fff;}
.ob-btn{background:#1B1F4B;color:#fff;border:none;border-radius:.7rem;padding:.7rem 1.2rem;font-weight:700;cursor:pointer;}
.ob-btn.ghost{background:#fff;color:#1B1F4B;border:1px solid #E4E1D6;}
</style>
<div class="ob max-w-5xl mx-auto px-4 py-8">
<h1 style="font-family:Manrope;font-weight:800;color:#1B1F4B;font-size:1.8rem" class="mb-2">Bulk Onboard</h1>
<p style="color:#64748B" class="mb-6">Paste CSV lines or upload a file: <code>username, role, grade</code> — one per line. Users are created with temporary passwords and joined to your school.</p>
<div class="ob-card">
<form method="post" action="/onboard/run/" enctype="multipart/form-data">
{% csrf_token %}
<textarea name="csv" placeholder="alice.kamau,learner,Grade 8&#10;brian.otieno,teacher,&#10;mary.wanjiku,learner,Form 2"></textarea>
<input type="file" name="file" accept=".csv,.txt" style="margin-top:.8rem">
<div style="display:flex;gap:.6rem;margin-top:1rem">
<button class="ob-btn" type="submit">Create users</button>
{% if results %}<a class="ob-btn ghost" href="/onboard/csv/" style="text-decoration:none;display:inline-flex;align-items:center">Download credentials CSV</a>{% endif %}
</div>
</form>
{% if results %}
<table><tr><th>Username</th><th>Role</th><th>Grade</th><th>Temporary password</th><th>Status</th></tr>
{% for r in results %}<tr><td>{{ r.username }}</td><td>{{ r.role }}</td><td>{{ r.grade }}</td><td><code>{{ r.password }}</code></td><td>{% if r.created %}created{% else %}existing{% endif %}</td></tr>{% endfor %}
</table>
{% endif %}
</div>
</div>
{% endblock %}''')
============ BLOCKER 4: Sovereignty Centre ============
w("apps/governance/centre_views.py", '''import json
import os
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from apps.audit.models import AuditEvent
from apps.institutions.models import Membership
from apps.learning.models import Conversation, Message
def _m(user):
return Membership.objects.filter(user=user, is_active=True).first()
@login_required(login_url="/accounts/login/")
def centre_page(request):
m = m(request.user)
inst = m.institution if m else None
consent = []
requests = []
try:
from apps.governance.models import ConsentRecord, DataRequest
consent = list(ConsentRecord.objects.filter(institution=inst).order_by("-id")[:20]) if inst else []
requests_ = list(DataRequest.objects.filter(institution=inst).order_by("-id")[:20]) if inst else []
except Exception:
pass
audit = list(AuditEvent.objects.filter(institution=inst).order_by("-id")[:30]) if inst else []
provider = getattr(inst, "ai_provider", "") or os.environ.get("AI_PROVIDER", "mock")
model = getattr(inst, "ai_model", "") or os.environ.get("OPENAI_MODEL", os.environ.get("OLLAMA_MODEL", "mock-dev-mode"))
retention = getattr(inst, "retention_days", 365)
return render(request, "governance/centre.html", {
"consent": consent, "requests": requests_, "audit": audit,
"provider": provider, "model": model, "retention": retention, "institution": inst})
@csrf_exempt
@login_required(login_url="/accounts/login/")
def centre_action(request):
if request.method != "POST":
return HttpResponse(status=405)
m = _m(request.user)
if not m:
return JsonResponse({"detail": "no institution"}, status=400)
data = json.loads(request.body or "{}")
act = data.get("action")
if act == "retention":
if hasattr(m.institution, "retention_days"):
m.institution.retention_days = int(data.get("days", 365))
m.institution.save()
return JsonResponse({"saved": True})
if act == "request":
try:
from apps.governance.models import DataRequest
drf = {f.name for f in DataRequest._meta.fields}
dk = {"institution": m.institution, "user": request.user}
for f in ("request_type", "type"):
if f in drf:
dk[f] = data.get("type", "export")
for f in ("status",):
if f in drf:
dk[f] = "pending"
DataRequest.objects.create(**{k: v for k, v in dk.items() if k in drf})
return JsonResponse({"created": True})
except Exception as e:
return JsonResponse({"detail": str(e)}, status=400)
if act == "delete":
convs = Conversation.objects.filter(user=request.user, institution=m.institution)
Message.objects.filter(conversation__in=convs).delete()
n = convs.count()
convs.delete()
AuditEvent.objects.create(institution=m.institution, actor=request.user, action="DATA_DELETED",
resource_type="User", resource_id=str(request.user.id),
metadata={"conversations": n})
return JsonResponse({"deleted": n})
return JsonResponse({"detail": "unknown action"}, status=400)
@login_required(login_url="/accounts/login/")
def centre_export(request):
m = _m(request.user)
convs = Conversation.objects.filter(user=request.user, institution=m.institution) if m else Conversation.objects.none()
payload = {
"user": request.user.username,
"institution": m.institution.name if m else "",
"conversations": [
{"title": c.title, "messages": [{"role": getattr(msg, "role", ""), "content": msg.content}
for msg in Message.objects.filter(conversation=c).order_by("id")]}
for c in convs],
}
resp = HttpResponse(json.dumps(payload, indent=2), content_type="application/json")
resp["Content-Disposition"] = 'attachment; filename="jifunze_my_data.json"'
return resp
''')
w("templates/governance/centre.html", '''{% extends "base.html" %}
{% block title %}Data Sovereignty Centre — JIFUNZE AI{% endblock %}
{% block content %}
<style>
.sv{font-family:Inter,sans-serif;color:#0F172A;}
.sv-card{background:#fff;border:1px solid #E4E1D6;border-radius:1rem;box-shadow:0 6px 18px -8px rgba(27,31,75,.14);padding:1.2rem 1.3rem;margin-bottom:1.1rem;}
.sv-card h3{font-family:Manrope;font-weight:800;color:#1B1F4B;font-size:1rem;margin-bottom:.7rem;display:flex;align-items:center;gap:.5rem;}
.sv table{width:100%;border-collapse:collapse;font-size:.78rem;}
.sv th,.sv td{border:1px solid #E4E1D6;padding:.45rem .55rem;text-align:left;vertical-align:top;}
.sv th{background:#1B1F4B;color:#fff;}
.sv-btn{background:#1B1F4B;color:#fff;border:none;border-radius:.6rem;padding:.55rem 1rem;font-weight:700;cursor:pointer;font-size:.8rem;}
.sv-btn.warn{background:#B91C1C;} .sv-btn.ghost{background:#fff;color:#1B1F4B;border:1px solid #E4E1D6;}
.chip{display:inline-block;font-size:.68rem;font-weight:700;padding:.2rem .6rem;border-radius:9999px;background:#EEF0F6;color:#3B4270;}
</style>
<div class="sv max-w-6xl mx-auto px-4 py-8">
<h1 style="font-family:Manrope;font-weight:800;color:#1B1F4B;font-size:1.9rem" class="mb-1">Data Sovereignty Centre</h1>
<p style="color:#64748B" class="mb-6">Your school owns its data. Here you control consent, retention, export, deletion and AI transparency.</p>
<div class="sv-card">
<h3>🤖 AI transparency</h3>
<p style="font-size:.85rem">Active provider: <span class="chip">{{ provider }}</span> &nbsp; Model: <span class="chip">{{ model }}</span></p>
<p style="font-size:.78rem;color:#64748B;margin-top:.4rem">Every AI operation is recorded in the audit trail below with provider and model identification.</p>
</div>
<div class="sv-card">
<h3>🗓 Retention policy</h3>
<form id="retForm" style="display:flex;gap:.6rem;align-items:center">
<input id="retDays" type="number" value="{{ retention }}" min="30" max="3650" style="width:110px;border:1px solid #E4E1D6;border-radius:.6rem;padding:.5rem">
<span style="font-size:.8rem;color:#64748B">days to retain audit + conversation data</span>
<button class="sv-btn" type="submit">Save</button>
</form>
</div>
<div class="sv-card">
<h3>✅ Consent records</h3>
{% if consent %}<table><tr><th>User</th><th>Policy</th><th>Granted</th><th>When</th></tr>
{% for c in consent %}<tr><td>{{ c.user }}</td><td>{{ c.policy_version|default:"v1.0" }}</td><td>{{ c.granted|default:"—" }}</td><td>{{ c.created_at|date:"d M Y" }}</td></tr>{% endfor %}</table>
{% else %}<p style="font-size:.82rem;color:#64748B">No consent records yet.</p>{% endif %}
</div>
<div class="sv-card">
<h3>📤 Data rights</h3>
<div style="display:flex;flex-wrap:wrap;gap:.6rem">
<a class="sv-btn ghost" style="text-decoration:none;display:inline-flex;align-items:center" href="/sovereignty/export/">Export my data (JSON)</a>
<button class="sv-btn" id="reqExport">Request export (workflow)</button>
<button class="sv-btn" id="reqDelete">Request deletion (workflow)</button>
<button class="sv-btn warn" id="doDelete">Delete my conversations now</button>
</div>
<p id="svMsg" style="font-size:.8rem;color:#0E9F6E;margin-top:.6rem"></p>
</div>
<div class="sv-card">
<h3>🧾 Data requests</h3>
{% if requests %}<table><tr><th>User</th><th>Type</th><th>Status</th><th>When</th></tr>
{% for r in requests %}<tr><td>{{ r.user }}</td><td>{{ r.request_type|default:r.type }}</td><td>{{ r.status }}</td><td>{{ r.created_at|date:"d M Y H:i" }}</td></tr>{% endfor %}</table>
{% else %}<p style="font-size:.82rem;color:#64748B">No requests yet.</p>{% endif %}
</div>
<div class="sv-card">
<h3>🔍 Audit trail (latest 30)</h3>
<table><tr><th>When</th><th>Actor</th><th>Action</th><th>Resource</th><th>Metadata</th></tr>
{% for a in audit %}<tr><td>{{ a.created_at|date:"d M H:i" }}</td><td>{{ a.actor|default:"system" }}</td><td>{{ a.action }}</td><td>{{ a.resource_type }} #{{ a.resource_id|truncatechars:8 }}</td><td style="font-size:.7rem">{{ a.metadata }}</td></tr>{% endfor %}
</table>
</div>
</div>
<script>
function csrf(){return (document.cookie.match(/csrftoken=([^;]+)/)||[])[1]||"";}
function post(action, extra){
return fetch("/sovereignty/action/",{method:"POST",credentials:"same-origin",headers:{"X-CSRFToken":csrf(),"Content-Type":"application/json"},body:JSON.stringify(Object.assign({action:action},extra||{}))})
.then(function(r){return r.json();});
}
document.getElementById("retForm").onsubmit=function(e){e.preventDefault();post("retention",{days:parseInt(document.getElementById("retDays").value,10)}).then(function(j){document.getElementById("svMsg").textContent="Retention saved.";});};
document.getElementById("reqExport").onclick=function(){post("request",{type:"export"}).then(function(){document.getElementById("svMsg").textContent="Export request logged.";location.reload();});};
document.getElementById("reqDelete").onclick=function(){post("request",{type:"delete"}).then(function(){document.getElementById("svMsg").textContent="Deletion request logged.";location.reload();});};
document.getElementById("doDelete").onclick=function(){if(!confirm("Permanently delete ALL your conversations and messages?"))return;post("delete").then(function(j){document.getElementById("svMsg").textContent="Deleted "+j.deleted+" conversation(s).";});};
</script>
{% endblock %}''')
============ URL wiring + nav repoint ============
up = base / "config/urls.py"
uc = up.read_text(encoding="utf-8")
if "bulk_views" not in uc:
uc = "from apps.accounts import bulk_views\nfrom apps.governance import centre_views\n" + uc
uc = re.sub(r'(path("api/learn/history/",[^)]*),)',
r'\1\n path("onboard/", bulk_views.onboard_page),\n path("onboard/run/", bulk_views.onboard_run),\n path("onboard/csv/", bulk_views.onboard_csv),\n path("sovereignty/", centre_views.centre_page),\n path("sovereignty/action/", centre_views.centre_action),\n path("sovereignty/export/", centre_views.centre_export),',
uc, count=1)
up.write_text(uc, encoding="utf-8")
bp = base / "templates/base.html"
bh = bp.read_text(encoding="utf-8")
bh = re.sub(r'href="[^"]"(?=[^>]>\sBulk Onboard)', 'href="/onboard/"', bh)
bh = re.sub(r'href="[^"]"(?=[^>]>\sSovereignty)', 'href="/sovereignty/"', bh)
bp.write_text(bh, encoding="utf-8")
print("CRITICAL BLOCKERS 1-4 INSTALLED: seeder, git files, bulk onboard, sovereignty centre")
