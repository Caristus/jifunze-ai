import uuid
from django.conf import settings
from django.db import models
class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey("institutions.Institution", on_delete=models.CASCADE, related_name="conversations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations")
    title = models.CharField(max_length=255, default="New Learning Session")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-updated_at"]
    def __str__(self):
        return f"{self.title} - {self.user.username}"
class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    model_provider = models.CharField(max_length=100, blank=True, help_text="e.g., ollama, openai")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["created_at"]
    def __str__(self):
        return f"{self.get_role_display()} message in {self.conversation.title}"
class MessageSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="sources")
    resource = models.ForeignKey("resources.LearningResource", on_delete=models.PROTECT)
    chunk = models.ForeignKey("resources.DocumentChunk", on_delete=models.PROTECT)
    relevance_score = models.FloatField(null=True, blank=True)
    def __str__(self):
        return f"Source for {self.message.id}"
