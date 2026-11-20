# JIFUNZE AI
**Intelligence for everyone. Knowledge without boundaries.**
An open-source, community-governed AI learning infrastructure for African schools,
educators and learners. Built for low-bandwidth reality, institutional data sovereignty
and transparent, source-grounded educational AI.
## Modules
- Learning Companion - AI learning assistant with source-grounded answers and citations.
- Teacher Studio - lesson plans, quizzes, worksheets and marking guides per curriculum.
- Data Sovereignty Centre - consent, audit trail, export and deletion workflows.
## Quickstart
    git clone https://github.com/carisokm2006/jifunze-ai.git
    cd jifunze-ai
    python -m venv venv
    venv\Scripts\Activate.ps1        # Windows
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    .\jifunze runserver              # Windows launcher
## Tests
    .\venv\Scripts\python.exe -m pytest tests -q
## Documentation
| Document | Purpose |
|---|---|
| docs/architecture.md | System design and tenancy invariant |
| docs/ai_transparency.md | Provider identification and grounding rules |
| docs/data_governance.md | Consent, export, deletion, audit |
| docs/privacy.md | Children's data and minimisation |
| docs/roadmap.md | 12-month plan |
## Licence
Apache License 2.0 (software). Documentation: CC-BY 4.0.
