from django.core.management.base import BaseCommand
from apps.learning.semantic import encode
from apps.resources.models import DocumentChunk
class Command(BaseCommand):
    help = "Populate DocumentChunk.embedding vectors for semantic search."
    def handle(self, *args, **o):
        n = 0
        for c in DocumentChunk.objects.all():
            if not c.embedding:
                c.embedding = encode(c.chunk_text or "")
                c.save(update_fields=["embedding"])
                n += 1
        self.stdout.write(self.style.SUCCESS("Embedded %d chunks." % n))
