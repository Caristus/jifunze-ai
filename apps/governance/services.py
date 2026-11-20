import json
from django.utils import timezone
from apps.learning.models import Conversation
from apps.teacher_studio.models import TeachingArtifact
from apps.audit.models import AuditEvent
from .models import ConsentRecord
def export_user_data(user, institution) -> dict:
    conversations = Conversation.objects.filter(user=user, institution=institution)
    return {
        "exported_at": timezone.now().isoformat(),
        "user": {
            "username": user.username,
            "role": user.role,
            "preferred_language": user.preferred_language,
        },
        "institution": institution.name,
        "conversations": [
            {
                "title": c.title,
                "created_at": c.created_at.isoformat(),
                "messages": [
                    {
                        "role": m.role,
                        "content": m.content,
                        "provider": m.model_provider,
                        "created_at": m.created_at.isoformat(),
                    }
                    for m in c.messages.all()
                ],
            }
            for c in conversations
        ],
        "teaching_artifacts": [
            {
                "type": a.artifact_type,
                "topic": a.topic,
                "created_at": a.created_at.isoformat(),
            }
            for a in TeachingArtifact.objects.filter(created_by=user, institution=institution)
        ],
        "consent_records": [
            {
                "purpose": c.purpose,
                "version": c.consent_version,
                "granted": c.granted,
                "recorded_at": c.recorded_at.isoformat(),
            }
            for c in ConsentRecord.objects.filter(user=user, institution=institution)
        ],
        "audit_events": [
            {
                "action": e.action,
                "resource_type": e.resource_type,
                "created_at": e.created_at.isoformat(),
            }
            for e in AuditEvent.objects.filter(actor=user, institution=institution)
        ],
    }
def execute_deletion(data_request) -> int:
    """Permanently delete the requester's learning data within the institution."""
    user = data_request.requested_by
    institution = data_request.institution
    conversations = Conversation.objects.filter(user=user, institution=institution)
    deleted = conversations.count()
    conversations.delete()
    TeachingArtifact.objects.filter(created_by=user, institution=institution).delete()
    return deleted
