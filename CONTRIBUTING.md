# Contributing to JIFUNZE AI
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
