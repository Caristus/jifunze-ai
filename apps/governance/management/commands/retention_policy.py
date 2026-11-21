from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.learning.models import Conversation
from apps.resources.models import LearningResource
from apps.teacher_studio.models import TeachingArtifact
from apps.audit.models import AuditEvent
from apps.institutions.models import Institution
class Command(BaseCommand):
    help = "Enforce data retention: delete records older than --days per scope."
    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=365)
        parser.add_argument("--scope", choices=["resources", "artifacts", "conversations", "all"], default="all")
        parser.add_argument("--institution", type=str, default="", help="Institution name filter (optional)")
        parser.add_argument("--dry-run", action="store_true")
    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=options["days"])
        inst_filter = {}
        if options["institution"]:
            inst = Institution.objects.filter(name__iexact=options["institution"]).first()
            if not inst:
                self.stderr.write(self.style.ERROR(f"Institution not found: {options['institution']}"))
                return
            inst_filter = {"institution": inst}
        report = {}
        scopes = ["resources", "artifacts", "conversations"] if options["scope"] == "all" else [options["scope"]]
        if "resources" in scopes:
            q = LearningResource.objects.filter(created_at__lt=cutoff, **inst_filter)
            report["resources"] = q.count()
            if not options["dry_run"]:
                q.delete()
        if "artifacts" in scopes:
            q = TeachingArtifact.objects.filter(created_at__lt=cutoff, **inst_filter)
            report["artifacts"] = q.count()
            if not options["dry_run"]:
                q.delete()
        if "conversations" in scopes:
            q = Conversation.objects.filter(created_at__lt=cutoff, **inst_filter)
            report["conversations"] = q.count()
            if not options["dry_run"]:
                q.delete()
        if not options["dry_run"]:
            AuditEvent.objects.create(
                institution=inst_filter.get("institution"),
                action="RETENTION_POLICY_RUN",
                metadata={"days": options["days"], "deleted": report},
            )
        verb = "would delete" if options["dry_run"] else "deleted"
        self.stdout.write(self.style.SUCCESS(f"Retention ({options['days']}d): {verb} {report}"))
