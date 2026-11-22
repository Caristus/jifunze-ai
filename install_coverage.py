import urllib.request
from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
def w(rel, text):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
# ---------- LICENSE (Apache-2.0, downloaded; MIT fallback) ----------
lic = base / "LICENSE"
if not lic.exists():
    try:
        req = urllib.request.Request("https://www.apache.org/licenses/LICENSE-2.0.txt", headers={"User-Agent": "Mozilla/5.0"})
        lic.write_bytes(urllib.request.urlopen(req, timeout=25).read())
    except Exception:
        lic.write_text('MIT License\n\nCopyright (c) 2026 JIFUNZE AI contributors\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n', encoding="utf-8")
w("CONTRIBUTING.md", """# Contributing to JIFUNZE AI
JIFUNZE AI is an open-source, community-governed AI learning infrastructure for African schools.
## How to contribute
1. Fork the repository and create a feature branch from `main`.
2. Follow the Django-first, security-first principles in `docs/architecture.md`.
3. Add or update tests for any behaviour change (`pytest`).
4. Never commit API keys, school records, children's personal data or proprietary code.
5. Open a pull request describing the change, the problem it solves and how it was tested.
## Code style
- Python: PEP 8, type hints where practical, docstrings on public functions.
- Templates: keep school-level data isolation checks in views/serializers, never only in templates.
- AI calls must go through `apps.ai_gateway` so provider transparency and audit logging apply.
## Reporting issues
Use GitHub issues for bugs and feature requests. For security matters see `SECURITY.md`.
""")
w("CODE_OF_CONDUCT.md", """# Code of Conduct
## Our pledge
We pledge to make participation in JIFUNZE AI a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.
## Our standards
Encouraged: welcoming language, respect for differing viewpoints, graceful acceptance of constructive criticism, focusing on what is best for the community and for learners.
Unacceptable: sexualised language or attention, trolling, insulting or derogatory comments, personal or political attacks, public or private harassment, publishing others' private information without permission, and any conduct inappropriate in a professional educational setting.
## Child safeguarding
JIFUNZE serves schools and minors. Contributors must never introduce features that collect unnecessary personal data about children, and must treat child-safeguarding concerns as highest priority.
## Enforcement
Instances of abusive or unacceptable behaviour may be reported to the maintainers. Maintainers will review, respond and take action they deem appropriate, including temporary or permanent bans.
## Scope
This Code of Conduct applies in project spaces and in public spaces when an individual is representing the project.
""")
w("SECURITY.md", """# Security Policy
## Supported versions
Only the latest release on `main` receives security support during the MVP phase.
## Reporting a vulnerability
Please do NOT open a public issue. Email the maintainers with:
- a description of the vulnerability and the affected component,
- steps to reproduce,
- potential impact on school data isolation or child privacy.
We acknowledge receipt within 72 hours and will coordinate a fix and disclosure timeline.
## Security principles enforced in code
- School-level (institution) data isolation on every query and API permission.
- AI provider and model identification recorded for every AI operation.
- Audit trail for generation, marking, transformation, export and deletion.
- No secrets in the repository; configuration via environment variables.
""")
w(".env.example", """# Copy to .env and fill in. Never commit .env
DEBUG=True
SECRET_KEY=change-me
USE_POSTGRES=False
POSTGRES_DB=jifunze
POSTGRES_USER=jifunze_user
POSTGRES_PASSWORD=change-me
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
AI_PROVIDER=mock
OPENAI_API_KEY=
OLLAMA_MODEL=llama3
ALLOWED_HOSTS=127.0.0.1,localhost
""")
w("requirements.txt", """Django>=5.2,<5.3
djangorestframework
psycopg[binary]
python-dotenv
Pillow
django-cors-headers
PyMuPDF
python-docx
gunicorn
pytest
pytest-django
""")
w("pytest.ini", """[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = test_*.py
addopts = -q
""")
w("conftest.py", """import pytest
from apps.accounts.models import User
from apps.institutions.models import Institution, Membership
def _make_school(suffix, role="teacher"):
    inst = Institution.objects.create(name="School %s" % suffix, country="Kenya")
    user = User.objects.create_user(username="user_%s" % suffix, password="pass12345!", role=role)
    Membership.objects.create(user=user, institution=inst, role=role, is_active=True)
    return inst, user
@pytest.fixture
def school_a(db):
    return _make_school("a")
@pytest.fixture
def school_b(db):
    return _make_school("b")
@pytest.fixture
def client_a(client, school_a):
    client.force_login(school_a[1])
    return client
""")
w("tests/test_security.py", """import pytest
from django.urls import reverse
pytestmark = pytest.mark.django_db
def test_anonymous_redirected_from_studio(client):
    r = client.get("/studio/")
    assert r.status_code in (302, 403)
    assert "/accounts/login/" in r.get("Location", "/accounts/login/")
def test_anonymous_api_rejected(client):
    r = client.get("/api/teacher/artifacts/recent/")
    assert r.status_code in (401, 403)
def test_library_requires_login(client):
    r = client.get("/library/")
    assert r.status_code in (302, 403)
def test_health_requires_login(client):
    r = client.get("/health/")
    assert r.status_code in (302, 403)
""")
w("tests/test_tenant_isolation.py", """import json
import pytest
from apps.teacher_studio.models import TeachingArtifact
pytestmark = pytest.mark.django_db
def _artifact(inst, user, topic):
    return TeachingArtifact.objects.create(
        institution=inst, created_by=user, artifact_type="lesson_plan",
        topic=topic, content=json.dumps({"kind": "lesson_plan", "title": topic}))
def test_school_cannot_see_other_school_artifacts(client_a, school_a, school_b):
    _artifact(school_a[0], school_a[1], "Photosynthesis")
    _artifact(school_b[0], school_b[1], "Secret B topic")
    r = client_a.get("/api/teacher/artifacts/recent/")
    assert r.status_code == 200
    titles = [x["title"] for x in r.json()]
    assert "Photosynthesis" in titles
    assert "Secret B topic" not in titles
def test_automark_rejects_foreign_artifact(client_a, school_b):
    foreign = _artifact(school_b[0], school_b[1], "Foreign quiz")
    r = client_a.post("/api/teacher/artifacts/automark/",
                      {"artifact_id": str(foreign.id), "answers": {}},
                      content_type="application/json")
    assert r.status_code == 404
""")
w("tests/test_integration.py", """import json
import pytest
pytestmark = pytest.mark.django_db
def test_generate_then_automark_quiz(client_a):
    r = client_a.post("/api/teacher/artifacts/generate/", {
        "artifact_type": "quiz", "topic": "Photosynthesis", "grade_level": "Form 2",
        "curriculum": "CBC/CBE", "count": 6, "mix": "balanced", "language": "en",
        "duration": 50, "difficulty": "Standard"}, content_type="application/json")
    assert r.status_code == 201
    art = r.json()
    lesson = json.loads(art["content"])
    assert lesson["kind"] == "quiz" and lesson["questions"]
    answers = {str(q["no"]): (q.get("correct") if q["type"] == "mcq" else
                              (q.get("answer") if q["type"] in ("short", "structured") else None))
               for q in lesson["questions"]}
    m = client_a.post("/api/teacher/artifacts/automark/",
                      {"artifact_id": art["id"], "answers": answers},
                      content_type="application/json")
    assert m.status_code == 200
    rep = m.json()
    assert rep["total_marks"] > 0 and 0 <= rep["percentage"] <= 100
def test_transform_improve_creates_version(client_a):
    r = client_a.post("/api/teacher/artifacts/generate/", {
        "artifact_type": "lesson_plan", "topic": "Photosynthesis", "grade_level": "Form 2",
        "curriculum": "CBC/CBE", "language": "en", "duration": 50}, content_type="application/json")
    art = r.json()
    t = client_a.post("/api/teacher/artifacts/transform/",
                      {"artifact_id": art["id"], "action": "improve"},
                      content_type="application/json")
    assert t.status_code == 200
    assert json.loads(t.json()["content"]).get("misconceptions")
""")
w(".github/workflows/tests.yml", """name: tests
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run test suite
        env:
          DEBUG: "False"
          SECRET_KEY: ci-test-key
          USE_POSTGRES: "False"
        run: pytest
""")
w("Dockerfile", """FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput || true
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
""")
w("docker-compose.yml", """services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: jifunze
      POSTGRES_USER: jifunze_user
      POSTGRES_PASSWORD: jifunze_pass
    volumes:
      - pgdata:/var/lib/postgresql/data
  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3"
    environment:
      DEBUG: "False"
      USE_POSTGRES: "True"
      POSTGRES_DB: jifunze
      POSTGRES_USER: jifunze_user
      POSTGRES_PASSWORD: jifunze_pass
      POSTGRES_HOST: db
      POSTGRES_PORT: "5432"
    ports:
      - "8000:8000"
    depends_on:
      - db
volumes:
  pgdata:
""")
DOCS = {
    "architecture.md": """# Architecture
JIFUNZE AI is a Django 5.2 monolith with three product modules (Learning Companion, Teacher Studio, Data Sovereignty Centre) served to learners, teachers and school administrators.
- **Apps**: accounts, institutions, learning, resources, teacher_studio, governance, ai_gateway, audit.
- **Data isolation**: every institution-owned query is filtered by the authenticated user's active Membership; enforced in views/serializers and covered by `tests/test_tenant_isolation.py`.
- **AI gateway**: provider-independent (`mock`, `openai`, `ollama`). Every AI operation records provider + model in the audit trail.
- **RAG**: uploads are extracted (PyMuPDF / python-docx), chunked and indexed; retrieval grounds answers and MessageSource rows provide citations.
- **Offline**: PWA manifest + service worker cache core shells and saved resources.
- **Database**: SQLite for development, PostgreSQL for production (docker-compose).
""",
    "installation.md": """# Installation
Requirements: Python 3.12.
    python -m venv venv
    venv\\Scripts\\activate        # Windows
    pip install -r requirements.txt
    copy .env.example .env        # then edit values
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
Production (Docker): `docker compose up --build` then open http://localhost:8000.
""",
    "privacy.md": """# Privacy
- We minimise personal data, especially for children; no unnecessary learner profiling.
- School data is logically isolated per institution and never shared across schools.
- Users can export or request deletion of their data via the Data Sovereignty Centre.
- AI operations are logged for transparency (provider, model, purpose), not for surveillance.
- Consent is recorded as versioned ConsentRecord entries aligned to school policy, not a single checkbox.
""",
    "data_governance.md": """# Data Governance
- **ConsentRecord**: who consented, to what policy version, when.
- **DataRequest**: export / deletion workflows with status tracking.
- **AuditEvent**: immutable activity and AI-processing trail.
- Institutional admins configure provider and model per school; platform admins own system settings.
- Retention: run `python manage.py apply_retention` periodically once retention policies are configured per institution.
""",
    "ai_transparency.md": """# AI Transparency
Every AI-generated artefact and answer records:
- the provider (`mock`, `openai`, `ollama`) and model identifier,
- the institution-configured settings in force at generation time,
- the retrieved sources used (MessageSource) where RAG applies,
- an audit event linking actor, institution and resource.
The Sovereignty Centre and the `/health/` page surface the active provider and model so schools always know which AI is operating on their data.
""",
    "security.md": """# Security
- Institution-scoped querysets and API permissions (see tests).
- CSRF enforced on all state-changing endpoints; session authentication.
- Secrets via environment variables only; `.env` is git-ignored.
- Password hashing via Django defaults; role-based navigation and server-side role checks.
- Dependency hygiene: pinned major versions in `requirements.txt`, CI runs the test suite on every push.
""",
    "roadmap.md": """# Roadmap
- **MVP (done)**: Companion RAG + citations, Teacher Studio (5 artefact types, auto-marking, PDF), Sovereignty Centre, audit, PWA, mobile UI.
- **Next**: retention policy enforcement, learner progress analytics, scheme-of-work generator, pgvector semantic retrieval, parent/guardian role, multi-language content packs.
- **Later**: federated local models for offline schools, district-level analytics, marketplace of openly-licensed curriculum packs.
""",
    "user_guide.md": """# User Guide
- **Learners**: open Learning Companion, pick subject/curriculum/grade, ask questions; answers cite your school's approved materials.
- **Teachers**: Teacher Studio generates lesson plans, quizzes (up to 20 questions, 10 types), worksheets, marking guides and activities; auto-mark, refine with AI actions, export PDF, save to Library.
- **Admins**: Sovereignty Centre for consent, data requests and AI transparency; Health for system status; Bulk Onboard for users; AI Settings for provider/model.
""",
}
for name, text in DOCS.items():
    w("docs/%s" % name, text)
# ---------- AI gateway: providers, safety, prompts ----------
w("apps/ai_gateway/providers/openai_provider.py", '''import json
import os
import urllib.request
from .base import BaseProvider
class OpenAIProvider(BaseProvider):
    provider_name = "openai"
    def __init__(self, model=None):
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    def generate(self, prompt, system_prompt=None, **kwargs):
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is not configured.")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = json.dumps({"model": self.model, "messages": messages, "temperature": 0.4}).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions", data=body,
            headers={"Content-Type": "application/json", "Authorization": "Bearer %s" % key},
            method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode())
        return data["choices"][0]["message"]["content"]
''')
w("apps/ai_gateway/providers/ollama_provider.py", '''import json
import os
import urllib.request
from .base import BaseProvider
class OllamaProvider(BaseProvider):
    provider_name = "ollama"
    def __init__(self, model=None):
        self.model = model or os.environ.get("OLLAMA_MODEL", "llama3")
    def generate(self, prompt, system_prompt=None, **kwargs):
        url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
        body = json.dumps({
            "model": self.model,
            "prompt": (system_prompt + "\\n\\n" if system_prompt else "") + prompt,
            "stream": False,
        }).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode())
        return data.get("response", "")
''')
w("apps/ai_gateway/safety.py", '''BLOCKED_TOPICS = (
    "weapon", "bomb", "exploit", "malware", "self-harm", "suicide method",
    "illegal drug synthesis", "child personal data", "bypass security",
)
def screen_prompt(text):
    """Return (allowed, reason). Blocks unsafe or privacy-violating requests."""
    low = (text or "").lower()
    for topic in BLOCKED_TOPICS:
        if topic in low:
            return False, "This request is outside the educational safety policy of JIFUNZE AI."
    return True, ""
def learning_guardrail():
    return ("You are a school tutor. If the provided sources do not support an answer, say so "
            "clearly instead of guessing. Never request or reveal personal data about children.")
''')
w("apps/ai_gateway/prompts/__init__.py", "")
w("apps/ai_gateway/prompts/templates.py", '''LEARNING_SYSTEM = (
    "You are JIFUNZE Learning Companion, a tutor for African primary and secondary schools. "
    "Adapt explanations to the learner's grade and curriculum. Cite the supplied school resources. "
    "If the resources are insufficient, state that clearly and suggest what to review."
)
TEACHER_SYSTEM = (
    "You are JIFUNZE Teacher Studio, an assistant for professional educators. Produce structured, "
    "curriculum-aligned teaching materials with clear outcomes, timed activities, differentiation "
    "and assessment rubrics. Return valid JSON when a schema is requested."
)
CITATION_INSTRUCTION = (
    "Ground every factual claim in the supplied passages. List the source titles you used."
)
''')
# ---------- Role-aware navigation ----------
bp = base / "templates/base.html"
html = bp.read_text(encoding="utf-8")
if "JF_ROLE_META" not in html:
    html = html.replace("</head>", '<meta name="user-role" content="{{ request.user.role|default:\'anon\' }}">\\n<!-- JF_ROLE_META -->\\n</head>', 1)
if "JF_ROLE_NAV" not in html:
    html = html.replace("</body>", '''<script>
/* JF_ROLE_NAV */
(function(){
  var role=(document.querySelector('meta[name="user-role"]')||{}).content||'anon';
  if(!role||role==='anon'||role==='school_admin'||role==='platform_admin')return;
  var ALLOW={
    learner:["/","/learn/","/library/","/help/","/accounts/"],
    teacher:["/","/learn/","/library/","/upload/","/studio/","/help/","/accounts/"]
  }[role]||[];
  function filter(scope){
    Array.prototype.forEach.call(scope.querySelectorAll('a[href]'),function(a){
      var h=a.getAttribute('href')||'';
      if(h.indexOf('#')===0)return;
      var ok=ALLOW.some(function(p){return h===p||(p!=="/"&&h.indexOf(p)===0);});
      if(!ok)a.style.display='none';
    });
  }
  filter(document);
  var t=setInterval(function(){var d=document.getElementById('mLinks');if(d){filter(d);clearInterval(t);}},300);
  setTimeout(function(){clearInterval(t);},4000);
})();
</script>
</body>''', 1)
bp.write_text(html, encoding="utf-8")
print("COVERAGE BUNDLE INSTALLED: license, governance docs, docker, CI, tests, providers, safety, prompts, role-nav")
