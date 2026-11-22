import json
from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
cmd_dir = base / "apps/resources/management/commands"
cmd_dir.mkdir(parents=True, exist_ok=True)
(base / "apps/resources/management/__init__.py").touch(exist_ok=True)
(cmd_dir / "__init__.py").touch(exist_ok=True)
CMD = '''import json
import re
import shutil
from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from apps.accounts.models import User
from apps.audit.models import AuditEvent
from apps.institutions.models import Institution
from apps.resources.models import DocumentChunk, LearningResource
CHUNK_SIZE = 1000
OVERLAP = 120
CURR_MAP = {"cbc": "CBC/CBE", "cbe": "CBC/CBE", "cbc-cbe": "CBC/CBE", "844": "8-4-4"}
def extract_text(path):
    if path.suffix.lower() == ".pdf":
        try:
            import pymupdf as fitz
        except Exception:
            import fitz
        doc = fitz.open(str(path))
        text = "\\n".join(page.get_text() for page in doc)
        doc.close()
        return text
    return path.read_text(encoding="utf-8-sig", errors="ignore")
def chunk_text(text):
    text = re.sub(r"\\s+", " ", text).strip()
    out = []
    i = 0
    while i < len(text):
        out.append(text[i:i + CHUNK_SIZE])
        i += CHUNK_SIZE - OVERLAP
    return [c for c in out if c.strip()]
def model_fields(model):
    return {f.name for f in model._meta.fields}
class Command(BaseCommand):
    help = "Import a curriculum pack (Curriculum/Grade/Subject/Topic/files) with provenance tiers A/B/C."
    def add_arguments(self, parser):
        parser.add_argument("pack_path")
        parser.add_argument("--institution", default="Jifunze Test School")
        parser.add_argument("--user", default="Caristus_Mugendi")
        parser.add_argument("--tier", default="A", choices=["A", "B", "C"])
        parser.add_argument("--license", default="")
        parser.add_argument("--attribution", default="")
        parser.add_argument("--week", default="")
        parser.add_argument("--term", default="")
        parser.add_argument("--dry-run", action="store_true")
    def handle(self, *args, **o):
        root = Path(o["pack_path"])
        if not root.is_dir():
            raise CommandError("Pack folder not found: %s" % root)
        inst = Institution.objects.filter(name=o["institution"]).first()
        user = User.objects.filter(username=o["user"]).first()
        if not inst or not user:
            raise CommandError("Institution or user not found.")
        lr = model_fields(LearningResource)
        dc = model_fields(DocumentChunk)
        manifest = {}
        mf = root / "manifest.json"
        if mf.exists():
            manifest = json.loads(mf.read_text(encoding="utf-8-sig"))
        counts = {"A": 0, "B": 0, "C": 0}
        processed = set()
        def save_resource(meta, curriculum, grade, subject, topic, title, tier, path=None):
            status = {"A": "ready", "B": "link", "C": "reference"}[tier]
            kwargs = {"institution": inst, "title": title, "status": status,
                      "uploaded_by": user, "subject": subject, "grade_level": grade,
                      "curriculum": curriculum, "topic": topic,
                      "week": meta.get("week", o["week"]), "term": meta.get("term", o["term"]),
                      "provenance_tier": tier, "license": meta.get("license", o["license"]),
                      "source_url": meta.get("source_url", ""), "attribution": meta.get("attribution", o["attribution"])}
            kwargs = {k: v for k, v in kwargs.items() if k in lr}
            lookup = {"institution": inst, "title": title}
            for f in ("grade_level", "subject", "topic", "curriculum"):
                if f in lr:
                    lookup[f] = kwargs.get(f, "")
            defaults = {k: v for k, v in kwargs.items() if k not in lookup}
            if o["dry_run"]:
                self.stdout.write("[dry] tier %s | %s / %s / %s / %s | %s" % (tier, curriculum, grade, subject, topic, title))
                counts[tier] += 1
                return None
            res, created = LearningResource.objects.update_or_create(defaults=defaults, **lookup)
            nchunks = 0
            if path is not None and tier in ("A", "C") and "file" in lr:
                dest_dir = Path(settings.MEDIA_ROOT) / "curriculum_pack" / curriculum.replace("/", "-") / grade / subject
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / path.name
                if not dest.exists():
                    shutil.copy2(path, dest)
                with open(dest, "rb") as fh:
                    res.file.save(path.name, File(fh), save=False)
            DocumentChunk.objects.filter(resource=res).delete()
            if tier == "A" and path is not None:
                for i, c in enumerate(chunk_text(extract_text(path))):
                    ck = {"resource": res, "chunk_index": i, "chunk_text": c}
                    ck = {k: v for k, v in ck.items() if k in dc or k == "resource"}
                    DocumentChunk.objects.create(**ck)
                    nchunks += 1
            res.save()
            try:
                AuditEvent.objects.create(institution=inst, actor=user, action="CURRICULUM_PACK_IMPORTED",
                    resource_type="LearningResource", resource_id=str(res.id),
                    metadata={"tier": tier, "license": kwargs.get("license", ""), "source_url": kwargs.get("source_url", ""),
                              "attribution": kwargs.get("attribution", ""), "chunks": nchunks,
                              "file": str(path.relative_to(root)) if path else ""})
            except Exception:
                pass
            counts[tier] += 1
            self.stdout.write(self.style.SUCCESS("imported tier %s: %s (%d chunks)" % (tier, title, nchunks)))
            return res
        for path in sorted(root.rglob("*")):
            if path.suffix.lower() not in (".pdf", ".txt", ".md"):
                continue
            rel = path.relative_to(root).parts
            curriculum = CURR_MAP.get(rel[0].lower(), rel[0]) if rel else "CBC/CBE"
            grade = rel[1] if len(rel) > 1 else ""
            subject = rel[2] if len(rel) > 2 else ""
            topic = rel[3] if len(rel) > 3 else path.stem
            meta = {}
            side = Path(str(path) + ".json")
            if side.exists():
                meta = json.loads(side.read_text(encoding="utf-8-sig"))
            key = str(path.relative_to(root)).replace("\\\\", "/")
            if key in manifest and isinstance(manifest[key], dict):
                meta = dict(manifest[key], **meta)
            tier = (meta.get("tier") or o["tier"]).upper()
            title = meta.get("title") or path.stem.replace("_", " ").replace("-", " ").title()
            processed.add(key)
            save_resource(meta, curriculum, grade, subject, topic, title, tier, path)
        for key, meta in manifest.items():
            if not isinstance(meta, dict) or meta.get("tier") != "B" or not meta.get("source_url"):
                continue
            if key in processed or (root / key).exists():
                continue
            save_resource(meta, meta.get("curriculum", "CBC/CBE"), meta.get("grade", ""), meta.get("subject", ""),
                          meta.get("topic", ""), meta.get("title", key), "B", None)
        self.stdout.write(self.style.SUCCESS("DONE tier A=%d B=%d C=%d" % (counts["A"], counts["B"], counts["C"])))
'''
(cmd_dir / "import_curriculum_pack.py").write_text(CMD, encoding="utf-8")
# --- add provenance fields to LearningResource (idempotent) ---
mp = base / "apps/resources/models.py"
content = mp.read_text(encoding="utf-8-sig")
if "provenance_tier" not in content:
    lines = content.splitlines(keepends=True)
    FIELDS = [
        'provenance_tier = models.CharField(max_length=1, choices=[("A","Ingest (open/licensed)"),("B","Link-out (cite only)"),("C","Reference-only (private)")], default="A")',
        'license = models.CharField(max_length=120, blank=True, default="")',
        'source_url = models.URLField(blank=True, default="")',
        'attribution = models.CharField(max_length=255, blank=True, default="")',
    ]
    for i, l in enumerate(lines):
        if l.strip().startswith("curriculum = models.CharField("):
            indent = l[:len(l) - len(l.lstrip())]
            lines[i+1:i+1] = [indent + f + "\\n" for f in FIELDS]
            break
    mp.write_text("".join(lines), encoding="utf-8")
    print("models: provenance fields added")
else:
    print("models: provenance fields already present")
# --- starter pack scaffold + manifest + sample + README ---
pack = base / "curriculum_pack"
for sub in ["CBC/Grade 8/Biology/Photosynthesis", "8-4-4/Form 2/Chemistry/Atomic Structure"]:
    (pack / sub).mkdir(parents=True, exist_ok=True)
sample = pack / "CBC/Grade 8/Biology/Photosynthesis/photosynthesis_notes.txt"
if not sample.exists():
    sample.write_text(
        "Photosynthesis is the process by which green plants convert light energy into chemical energy. "
        "It occurs in chloroplasts, where chlorophyll absorbs mainly red and blue light. "
        "The overall equation is 6CO2 + 6H2O + light -> C6H12O6 + 6O2. "
        "Light-dependent reactions split water and produce ATP and NADPH; the Calvin cycle fixes carbon dioxide into glucose. "
        "This original sample note is released CC0 for demonstration.", encoding="utf-8")
manifest = {
    "CBC/Grade 8/Biology/Photosynthesis/photosynthesis_notes.txt": {"tier": "A", "license": "CC0 (original sample)", "attribution": "JIFUNZE AI"},
    "knec-2024-biology-paper1": {"tier": "B", "title": "KCSE 2024 Biology Paper 1 (KNEC)", "curriculum": "8-4-4", "grade": "Form 4", "subject": "Biology", "topic": "Exams", "source_url": "https://www.knec.ac.ke/downloads/", "license": "KNEC (link-out, all rights reserved)", "attribution": "Kenya National Examinations Council"},
}
(pack / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
readme = "\n".join([
    "# Curriculum Pack",
    "",
    "Folder convention: <Curriculum>/<Grade>/<Subject>/<Topic>/<files.pdf|.txt|.md>",
    "Curriculum folders: CBC, CBE, 8-4-4, Cambridge IGCSE, IB, CAPS, ...",
    "",
    "Provenance tiers (set per file via manifest.json or <file>.json sidecar, or --tier):",
    "  A = Ingest: open/licensed PDFs (KICD designs, CC/OER, your own). Extracted + chunked + searchable.",
    "  B = Link-out: proprietary (KNEC papers, paid-site notes). NOT copied; stored as a citation + source_url.",
    "  C = Reference-only: your private downloaded copies. Stored, NOT put in the learner RAG index.",
    "",
    "Put legally-obtained PDFs here (KICD curriculum designs, KNEC via licence/link, OER, your own).",
    "Do NOT place scraped paid-site corpora in tier A.",
    "",
    "Run:",
    "  .\\jifunze import_curriculum_pack curriculum_pack --dry-run",
    "  .\\jifunze import_curriculum_pack curriculum_pack",
])
(pack / "README.md").write_text(readme, encoding="utf-8")
print("SCAFFOLD READY at curriculum_pack/")
