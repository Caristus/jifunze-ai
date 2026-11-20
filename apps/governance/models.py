import uuid
from django.conf import settings
from django.db import models
class ConsentRecord(models.Model):
    class Purpose(models.TextChoices):
        AI_PROCESSING = "ai_processing", "AI-assisted learning processing"
        DATA_RETENTION = "data_retention", "Retention of learning records"
        RESEARCH = "research", "Anonymised educational research"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey("institutions.Institution", on_delete=models.CASCADE, related_name="consent_records")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consent_records")
    purpose = models.CharField(max_length=150, choices=Purpose.choices, default=Purpose.AI_PROCESSING)
    consent_version = models.CharField(max_length=50, default="v1.0")
    granted = models.BooleanField(default=False)
    guardian_name = models.CharField(max_length=150, blank=True, help_text="Only for learners who are minors.")
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="consent_recorded_by")
    recorded_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ["-recorded_at"]
    def __str__(self):
        state = "granted" if self.granted else "not granted"
        return f"{self.user.username} - {self.get_purpose_display()} ({state})"
class DataRequest(models.Model):
    class RequestType(models.TextChoices):
        EXPORT = "export", "Data Export"
        DELETION = "deletion", "Data Deletion"
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey("institutions.Institution", on_delete=models.CASCADE, related_name="data_requests")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="data_requests")
    request_type = models.CharField(max_length=20, choices=RequestType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="data_requests_resolved")
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.get_request_type_display()} by {self.requested_by.username} ({self.get_status_display()})"
