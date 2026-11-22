from django.db import models
from django.contrib.auth import get_user_model
import uuid
User = get_user_model()
class Institution(models.Model):
    """Educational institution (school, learning center, etc.)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    retention_days = models.IntegerField(default=365, help_text="Days to retain audit and conversation data")
    require_approval = models.BooleanField(default=False, help_text="New teacher/learner uploads require admin approval")
    slug = models.SlugField(unique=True, blank=True)
    country = models.CharField(max_length=100, default="Kenya")
    institution_type = models.CharField(
        max_length=50,
        choices=[
            ("primary", "Primary School"),
            ("secondary", "Secondary School"),
            ("university", "University"),
            ("training_center", "Training Center"),
        ],
        default="secondary"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # AI configuration
    AI_PROVIDER_CHOICES = [
        ("mock", "Development Mock (No AI)"),
        ("ollama", "Ollama (Local Inference)"),
    ]
    ai_provider = models.CharField(
        max_length=50,
        choices=AI_PROVIDER_CHOICES,
        default="mock",
        help_text="Which AI backend to use for this institution"
    )
    ai_model = models.CharField(
        max_length=100,
        blank=True,
        help_text="Model name for Ollama (e.g., llama3.2, mistral)"
    )
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
class Membership(models.Model):
    """User membership in an institution with role-based access."""
    ROLE_CHOICES = [
        ("school_admin", "School Administrator"),
        ("teacher", "Teacher"),
        ("learner", "Learner"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="learner")
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ["user", "institution"]
        ordering = ["-joined_at"]
    def __str__(self):
        return f"{self.user.username} @ {self.institution.name} ({self.get_role_display()})"
