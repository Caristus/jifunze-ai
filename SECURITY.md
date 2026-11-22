# Security Policy
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
