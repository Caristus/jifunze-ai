# Security
- Institution-scoped querysets and API permissions (see tests).
- CSRF enforced on all state-changing endpoints; session authentication.
- Secrets via environment variables only; `.env` is git-ignored.
- Password hashing via Django defaults; role-based navigation and server-side role checks.
- Dependency hygiene: pinned major versions in `requirements.txt`, CI runs the test suite on every push.
