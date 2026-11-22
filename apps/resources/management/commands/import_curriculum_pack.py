import json
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
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text
    return path.read_text(encoding="utf-8-sig", errors="ignore")
def chunk_text(text):
    text = re.sub(r"\s+", " ", text).strip()
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
            key = str(path.relative_to(root)).replace("\\", "/")
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
