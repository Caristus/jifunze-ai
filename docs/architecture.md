# Architecture
JIFUNZE AI is a Django 5.2 monolith with three product modules (Learning Companion, Teacher Studio, Data Sovereignty Centre) served to learners, teachers and school administrators.
- **Apps**: accounts, institutions, learning, resources, teacher_studio, governance, ai_gateway, audit.
- **Data isolation**: every institution-owned query is filtered by the authenticated user's active Membership; enforced in views/serializers and covered by `tests/test_tenant_isolation.py`.
- **AI gateway**: provider-independent (`mock`, `openai`, `ollama`). Every AI operation records provider + model in the audit trail.
- **RAG**: uploads are extracted (PyMuPDF / python-docx), chunked and indexed; retrieval grounds answers and MessageSource rows provide citations.
- **Offline**: PWA manifest + service worker cache core shells and saved resources.
- **Database**: SQLite for development, PostgreSQL for production (docker-compose).
