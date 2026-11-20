import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    """JIFUNZE AI platform user. Data-minimised by design."""
    class Role(models.TextChoices):
        ADMIN = "admin", "Platform Administrator"
        SCHOOL_ADMIN = "school_admin", "School Administrator"
        TEACHER = "teacher", "Teacher"
        LEARNER = "learner", "Learner"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.LEARNER)
    preferred_language = models.CharField(max_length=10, default="en")
    is_minor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["username"]
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
