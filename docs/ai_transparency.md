# AI Transparency
Every AI-generated artefact and answer records:
- the provider (`mock`, `openai`, `ollama`) and model identifier,
- the institution-configured settings in force at generation time,
- the retrieved sources used (MessageSource) where RAG applies,
- an audit event linking actor, institution and resource.
The Sovereignty Centre and the `/health/` page surface the active provider and model so schools always know which AI is operating on their data.
