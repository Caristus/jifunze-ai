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
    CURRICULUM_CHOICES = [
        ("CBC/CBE", "Kenya CBC/CBE"), ("8-4-4", "Kenya 8-4-4"),
        ("Cambridge IGCSE", "Cambridge IGCSE/A-Level"), ("IB", "International Baccalaureate"),
        ("CAPS", "South Africa CAPS"), ("NECTA", "Tanzania NECTA"), ("NCDC", "Uganda NCDC"),
        ("NERDC", "Nigeria NERDC"), ("NaCCA", "Ghana NaCCA"), ("ZIMSEC", "Zimbabwe ZIMSEC"),
        ("WAEC", "West Africa WAEC"), ("Edexcel", "Edexcel International"), ("Common Core", "USA Common Core"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey("institutions.Institution", on_delete=models.CASCADE, related_name="artifacts")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="artifacts")
    artifact_type = models.CharField(max_length=30, choices=ArtifactType.choices, default=ArtifactType.LESSON_PLAN)
    topic = models.CharField(max_length=255)
    grade_level = models.CharField(max_length=50, blank=True)
    curriculum = models.CharField(max_length=100, choices=CURRICULUM_CHOICES, default="CBC/CBE")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.get_artifact_type_display()} - {self.topic}"
