# Data Governance Framework
## Ownership
Educational data belongs to the institution that produces it. JIFUNZE is a custodian, not an owner.
## Consent
- Recorded per purpose (AI processing, retention, research) with a policy version.
- Withdrawable at any time; withdrawal is timestamped and audited.
- For minors, a guardian name field supports guardian-authorised consent. A checkbox alone is never a complete consent system; school policy and applicable law govern.
## Data rights workflows
- Export: any member can download their full data as JSON (conversations, messages, artifacts, consent, audit history).
- Deletion: request -> pending -> approved/completed/rejected. Completion permanently deletes the requester's conversations and artifacts within the institution and records the deletion count in the audit trail.
- Only School Administrators and Platform Administrators may resolve requests.
## Audit
Every AI query, upload, generation, consent change, export and deletion writes an AuditEvent
(actor, action, resource, metadata, timestamp). The audit trail is retained for accountability
even after personal data deletion.
