# Curriculum Pack

Folder convention: <Curriculum>/<Grade>/<Subject>/<Topic>/<files.pdf|.txt|.md>
Curriculum folders: CBC, CBE, 8-4-4, Cambridge IGCSE, IB, CAPS, ...

Provenance tiers (set per file via manifest.json or <file>.json sidecar, or --tier):
  A = Ingest: open/licensed PDFs (KICD designs, CC/OER, your own). Extracted + chunked + searchable.
  B = Link-out: proprietary (KNEC papers, paid-site notes). NOT copied; stored as a citation + source_url.
  C = Reference-only: your private downloaded copies. Stored, NOT put in the learner RAG index.

Put legally-obtained PDFs here (KICD curriculum designs, KNEC via licence/link, OER, your own).
Do NOT place scraped paid-site corpora in tier A.

Run:
  .\jifunze import_curriculum_pack curriculum_pack --dry-run
  .\jifunze import_curriculum_pack curriculum_pack