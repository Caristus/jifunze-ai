import uuid
from django.conf import settings
from django.db import models
class TeachingArtifact(models.Model):
    class ArtifactType(models.TextChoices):
        LESSON_PLAN = "lesson_plan", "Lesson Plan"
        QUIZ = "quiz", "Quiz"
        WORKSHEET = "worksheet", "Worksheet"
        MARKING_GUIDE = "marking_guide", "Marking Guide"
        ACTIVITY = "activity", "Learning Activity"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey("institutions.Institution", on_delete=models.CASCADE, related_name="teaching_artifacts")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_artifacts")
    artifact_type = models.CharField(max_length=30, choices=ArtifactType.choices)
    topic = models.CharField(max_length=255)
    grade_level = models.CharField(max_length=50, blank=True)
    curriculum = models.CharField(max_length=50, default="CBC/CBE", help_text="CBC/CBE, Cambridge IGCSE, 8-4-4, etc.")
    content = models.TextField(help_text="The generated AI content (Markdown/HTML)")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.get_artifact_type_display()}: {self.topic}"

