# JIFUNZE AI - development access card
Development / demo seed accounts only. Reset any time with:
`.\venv\Scripts\python.exe reset_access.py`
| Username | Password | Role | Where it signs in |
|---|---|---|---|
| Caristus_Mugendi | admin12345! | platform_admin (superuser) | /accounts/login/ and /admin/ |
| admin | admin12345! | platform_admin (superuser) | /accounts/login/ and /admin/ |
| jifunze.admin | Jifunze@2026! | platform_admin (superuser) | /accounts/login/ and /admin/ |
| teacher.demo | teach12345! | teacher | /accounts/login/ only |
| learner.demo | learn12345! | learner | /accounts/login/ only |
| parent.demo | parent12345! | parent (ward: learner.demo) | /accounts/login/ only |
Notes
- /admin/ accepts staff/superuser accounts only (first three rows). Teacher, learner and parent accounts are deliberately rejected there.
- The sign-in page shows one-click demo chips while DEBUG=True; they fill and submit these same credentials.
- reset_access.py also clears any 2FA secret and re-activates the accounts, so a locked or forgotten password never blocks a demo.
