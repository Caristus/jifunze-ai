import uuid
from django.conf import settings
from django.db import models
from apps.accounts.models import User
class Institution(models.Model):
    """A school or educational organisation. The tenant boundary."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100, default="Kenya")
    institution_type = models.CharField(max_length=50, default="school")
    curriculum = models.CharField(max_length=100, blank=True, help_text="e.g. CBC/CBE, Cambridge")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return self.name
class Membership(models.Model):
    """Links a user to an institution with an institution-scoped role."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=User.Role.choices, default=User.Role.LEARNER)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["institution__name", "user__username"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "institution"],
                name="unique_user_per_institution",
            )
        ]
        indexes = [
            models.Index(fields=["institution", "role"]),
        ]
    def __str__(self):
        return f"{self.user.username} @ {self.institution.name} ({self.get_role_display()})"
