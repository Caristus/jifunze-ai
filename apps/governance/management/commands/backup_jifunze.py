import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand
from django.core.management import call_command
from apps.institutions.models import Institution
class Command(BaseCommand):
    help = "Create a timestamped backup: JSON data dump + media archive."
    def add_arguments(self, parser):
        parser.add_argument("--institution", type=str, default="")
    def handle(self, *args, **options):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = Path(settings.BASE_DIR) / "backups"
        backup_dir.mkdir(exist_ok=True)
        # Data dump (scoped if institution given)
        data = {"institutions": json.loads(serializers.serialize("json", [Institution.objects.get(name__iexact=options["institution"])])) if options["institution"] else json.loads(serializers.serialize("json", Institution.objects.all()))}
        dump_path = backup_dir / f"jifunze-data-{stamp}.json"
        dump_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        # Media archive
        zip_path = backup_dir / f"jifunze-media-{stamp}.zip"
        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists():
            shutil.make_archive(str(zip_path.with_suffix("")), "zip", media_root)
        self.stdout.write(self.style.SUCCESS(f"Backup created: {dump_path.name}, {zip_path.name}"))
