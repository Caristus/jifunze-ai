# AI Transparency Statement
## Principles
1. Provider independence. JIFUNZE never locks a school into one AI vendor.
2. Always identified. Every AI message stores model_provider; every AI operation writes an AuditEvent.
3. Source-grounded. Answers are generated from the school's approved resources and returned with citations.
4. Honest uncertainty. When retrieved context is insufficient, the system says so instead of fabricating confidence.
5. No training on learners. School data answers that school's queries only.
## Current configuration
Development deployments run in mock_dev_mode unless AI_PROVIDER, AI_MODEL and AI_API_KEY
are configured in .env. The active provider is displayed in every response and in the
Data Sovereignty Centre audit trail.
## Known limitations
- Retrieval is lexical/institution-scoped in the MVP; semantic (pgvector) retrieval is roadmap Phase 1.
- Local inference is optional and hardware-dependent; the platform degrades gracefully without it.
