import uuid
from django.conf import settings
from django.db import models
class LearningResource(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Uploaded"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey("institutions.Institution", on_delete=models.CASCADE, related_name="resources")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploaded_resources")
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=100, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    topic = models.CharField(max_length=255, blank=True, help_text="Folder hierarchy, e.g. Biology > Form 2")
    curriculum = models.CharField(max_length=100, blank=True, default="CBC/CBE")
    provenance_tier = models.CharField(max_length=1, choices=[("A","Ingest (open/licensed)"),("B","Link-out (cite only)"),("C","Reference-only (private)")], default="A")
    license = models.CharField(max_length=120, blank=True, default="")
    source_url = models.URLField(blank=True, default="")
    attribution = models.CharField(max_length=255, blank=True, default="")
    file = models.FileField(upload_to="resources/%Y/%m/")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return self.title
class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE, related_name="chunks")
    chunk_text = models.TextField()
    chunk_index = models.IntegerField(default=0)
    # Semantic embeddings activate only when USE_POSTGRES=True (pgvector).
    # On SQLite this stays null; keyword retrieval (retrieval.py) handles grounding.
    embedding = models.JSONField(null=True, blank=True, help_text="pgvector embedding when PostgreSQL is enabled")
    class Meta:
        ordering = ["chunk_index"]
    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.resource.title}"

