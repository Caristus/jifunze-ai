
## One-click run

- **Windows Explorer:** double-click `run.cmd` (or `run-lan.cmd` for phone access).
- **Terminal:** `.\run.ps1` &nbsp;|&nbsp; phone: `.\run.ps1 -Lan` &nbsp;|&nbsp; custom port: `.\run.ps1 -Port 8080`
- **VS Code:** `Ctrl+Shift+B` runs the server task; `F5` starts it under the debugger.
- **Fresh clone:** `git clone <repo> && cd jifunze-ai && .\run.ps1` - creates the venv, installs deps, migrates and opens the browser.
﻿# JIFUNZE AI
**Intelligence for everyone. Knowledge without boundaries.**
An open-source, community-governed AI learning infrastructure for African schools.
## Three modules
- **Learning Companion** — level-aware AI tutor grounded in your school's approved materials, with source citations and open-knowledge fallback.
- **Teacher Studio** — lesson plans, schemes of work, quizzes (10 question types, auto-marking), worksheets, marking guides, activities and revision notes; AI refine actions; branded PDF export.
- **Data Sovereignty Centre** — consent records, data export/deletion workflows, AI provider transparency, retention policy and a full audit trail.
## Quick start
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    copy .env.example .env
    python manage.py migrate
    python manage.py seed_demo
    python manage.py runserver
Open http://127.0.0.1:8000 and sign in with dmin / admin12345! (created by seed_demo).
## Mobile
Run python manage.py runserver 0.0.0.0:8000, open the printed LAN IP on a phone on the same Wi-Fi, then **Add to Home Screen** for the PWA.
## Documentation
See docs/ for architecture, installation, privacy, data governance, AI transparency, security, roadmap and user guide.
## Licence
Apache-2.0 (software) · CC-BY-4.0 (documentation).
