# JIFUNZE AI - Technical Architecture
## Overview
JIFUNZE AI is a multi-tenant, open-source educational AI platform for African schools.
Three product modules (Learning Companion, Teacher Studio, Data Sovereignty Centre)
share one Django 5.2 LTS backend with a provider-independent AI gateway.
## System layers
1. Web application - server-rendered Django templates + Tailwind CSS + vanilla JS.
2. REST API - Django REST Framework, session authentication, CSRF-protected.
3. Engines - Learning (RAG conversations), Teacher (artifact generation), Governance (consent, audit, export, deletion).
4. AI Gateway - adapter pattern; hosted providers or local inference (Ollama); mock mode for offline development.
5. Persistence - PostgreSQL in production (SQLite for local dev); school-scoped records; pgvector on the roadmap.
## Multi-tenancy rule (security invariant)
Every institution-owned query is filtered by the authenticated user's active Membership.
No view may query school data without this filter. Enforced by tests/test_tenant_isolation.py.
## RAG pipeline
upload -> extract (PyMuPDF / python-docx) -> chunk (paragraph-aware) -> index ->
retrieve (institution-scoped) -> generate (grounded prompt) -> cite (MessageSource) -> audit.
## Applications
| App | Responsibility |
|---|---|
| accounts | Custom user, roles, dashboards |
| institutions | Schools, memberships, tenant boundary |
| resources | Uploads, extraction, chunking |
| learning | Conversations, messages, citations |
| teacher_studio | Lesson plans, quizzes, guides |
| governance | Consent, data requests, export, deletion |
| ai_gateway | Provider abstraction, prompts, safety |
| audit | Immutable processing trail |
