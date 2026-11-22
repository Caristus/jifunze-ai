# Data Governance
- **ConsentRecord**: who consented, to what policy version, when.
- **DataRequest**: export / deletion workflows with status tracking.
- **AuditEvent**: immutable activity and AI-processing trail.
- Institutional admins configure provider and model per school; platform admins own system settings.
- Retention: run `python manage.py apply_retention` periodically once retention policies are configured per institution.
