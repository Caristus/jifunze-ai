import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.audit.models import AuditEvent
from apps.institutions.models import Membership
from .models import ConsentRecord, DataRequest
from .serializers import ConsentRecordSerializer, DataRequestSerializer
from . import services
ADMIN_ROLES = ("school_admin", "admin")
def _membership(user):
    return Membership.objects.filter(user=user, is_active=True).first()
@login_required(login_url="/accounts/login/")
def centre_page(request):
    membership = _membership(request.user)
    institution = membership.institution if membership else None
    context = {
        "membership": membership,
        "is_admin": request.user.role in ADMIN_ROLES,
        "events": AuditEvent.objects.filter(institution=institution)[:100] if institution else AuditEvent.objects.none(),
        "consents": ConsentRecord.objects.filter(institution=institution)[:100] if institution else ConsentRecord.objects.none(),
        "requests": DataRequest.objects.filter(institution=institution)[:100] if institution else DataRequest.objects.none(),
    }
    return render(request, "governance/centre.html", context)
class ConsentViewSet(viewsets.ModelViewSet):
    serializer_class = ConsentRecordSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        membership = _membership(self.request.user)
        if not membership:
            return ConsentRecord.objects.none()
        if self.request.user.role in ADMIN_ROLES:
            return ConsentRecord.objects.filter(institution=membership.institution)
        return ConsentRecord.objects.filter(institution=membership.institution, user=self.request.user)
    def perform_create(self, serializer):
        membership = _membership(self.request.user)
        serializer.save(user=self.request.user, institution=membership.institution, recorded_by=self.request.user)
        AuditEvent.objects.create(
            institution=membership.institution, actor=self.request.user,
            action="CONSENT_RECORDED", resource_type="ConsentRecord",
            resource_id=str(serializer.instance.id),
            metadata={"purpose": serializer.instance.purpose, "granted": serializer.instance.granted})
    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        record = self.get_object()
        record.granted = False
        record.withdrawn_at = timezone.now()
        record.save()
        AuditEvent.objects.create(
            institution=record.institution, actor=request.user,
            action="CONSENT_WITHDRAWN", resource_type="ConsentRecord", resource_id=str(record.id))
        return Response(ConsentRecordSerializer(record).data)
class DataRequestViewSet(viewsets.ModelViewSet):
    serializer_class = DataRequestSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]
    def get_queryset(self):
        membership = _membership(self.request.user)
        if not membership:
            return DataRequest.objects.none()
        if self.request.user.role in ADMIN_ROLES:
            return DataRequest.objects.filter(institution=membership.institution)
        return DataRequest.objects.filter(institution=membership.institution, requested_by=self.request.user)
    def perform_create(self, serializer):
        membership = _membership(self.request.user)
        serializer.save(requested_by=self.request.user, institution=membership.institution)
        AuditEvent.objects.create(
            institution=membership.institution, actor=self.request.user,
            action="DATA_REQUEST_SUBMITTED", resource_type="DataRequest",
            resource_id=str(serializer.instance.id),
            metadata={"type": serializer.instance.request_type})
    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        data_request = self.get_object()
        if request.user.role not in ADMIN_ROLES:
            return Response({"detail": "Only school administrators can resolve data requests."}, status=status.HTTP_403_FORBIDDEN)
        decision = request.data.get("decision")
        if decision not in ("approved", "completed", "rejected"):
            return Response({"detail": "decision must be approved, completed or rejected"}, status=status.HTTP_400_BAD_REQUEST)
        detail = {}
        if decision == "completed" and data_request.request_type == DataRequest.RequestType.DELETION:
            detail = {"conversations_deleted": services.execute_deletion(data_request)}
        data_request.status = decision
        data_request.resolved_at = timezone.now()
        data_request.resolved_by = request.user
        data_request.save()
        AuditEvent.objects.create(
            institution=data_request.institution, actor=request.user,
            action=f"DATA_REQUEST_{decision.upper()}", resource_type="DataRequest",
            resource_id=str(data_request.id), metadata=detail)
        return Response(DataRequestSerializer(data_request).data)
@login_required(login_url="/accounts/login/")
def export_my_data(request):
    membership = _membership(request.user)
    if not membership:
        return JsonResponse({"error": "No institution membership"}, status=403)
    payload = services.export_user_data(request.user, membership.institution)
    AuditEvent.objects.create(
        institution=membership.institution, actor=request.user,
        action="DATA_EXPORT_SELF", resource_type="User", resource_id=str(request.user.id))
    response = HttpResponse(json.dumps(payload, indent=2, default=str), content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="jifunze-export-{request.user.username}.json"'
    return response
@login_required(login_url="/accounts/login/")
def system_health(request):
    from django.db import connection
    from pathlib import Path
    import json
    from apps.resources.models import LearningResource, DocumentChunk
    from apps.learning.models import Conversation, Message
    from apps.teacher_studio.models import TeachingArtifact
    from apps.governance.models import ConsentRecord, DataRequest
    from apps.audit.models import AuditEvent
    membership = _membership(request.user)
    institution = membership.institution if membership else None
    backups = sorted((Path(settings.BASE_DIR) / "backups").glob("*"), reverse=True) if (Path(settings.BASE_DIR) / "backups").exists() else []
    context = {
        "institution": institution,
        "counts": {
            "resources": LearningResource.objects.filter(institution=institution).count() if institution else LearningResource.objects.count(),
            "chunks": DocumentChunk.objects.filter(resource__institution=institution).count() if institution else DocumentChunk.objects.count(),
            "conversations": Conversation.objects.filter(institution=institution).count() if institution else Conversation.objects.count(),
            "messages": Message.objects.filter(conversation__institution=institution).count() if institution else Message.objects.count(),
            "artifacts": TeachingArtifact.objects.filter(institution=institution).count() if institution else TeachingArtifact.objects.count(),
            "consents": ConsentRecord.objects.filter(institution=institution).count() if institution else ConsentRecord.objects.count(),
            "requests": DataRequest.objects.filter(institution=institution).count() if institution else DataRequest.objects.count(),
            "audit": AuditEvent.objects.filter(institution=institution).count() if institution else AuditEvent.objects.count(),
        },
        "db_engine": connection.vendor,
        "ai_provider": getattr(institution, "ai_provider", "mock") if institution else "mock",
        "ai_model": getattr(institution, "ai_model", "") if institution else "",
        "pwa": {
            "manifest": (Path(settings.STATICFILES_DIRS[0]) / "manifest.json").exists(),
            "service_worker": (Path(settings.STATICFILES_DIRS[0]) / "sw.js").exists(),
        },
        "last_backup": backups[0].name if backups else None,
    }
    return render(request, "governance/health.html", context)
@login_required(login_url="/accounts/login/")
def system_health(request):
    from django.db import connection
    from pathlib import Path
    import json
    from apps.resources.models import LearningResource, DocumentChunk
    from apps.learning.models import Conversation, Message
    from apps.teacher_studio.models import TeachingArtifact
    from apps.governance.models import ConsentRecord, DataRequest
    from apps.audit.models import AuditEvent
    membership = _membership(request.user)
    institution = membership.institution if membership else None
    backups = sorted((Path(settings.BASE_DIR) / "backups").glob("*"), reverse=True) if (Path(settings.BASE_DIR) / "backups").exists() else []
    context = {
        "institution": institution,
        "counts": {
            "resources": LearningResource.objects.filter(institution=institution).count() if institution else LearningResource.objects.count(),
            "chunks": DocumentChunk.objects.filter(resource__institution=institution).count() if institution else DocumentChunk.objects.count(),
            "conversations": Conversation.objects.filter(institution=institution).count() if institution else Conversation.objects.count(),
            "messages": Message.objects.filter(conversation__institution=institution).count() if institution else Message.objects.count(),
            "artifacts": TeachingArtifact.objects.filter(institution=institution).count() if institution else TeachingArtifact.objects.count(),
            "consents": ConsentRecord.objects.filter(institution=institution).count() if institution else ConsentRecord.objects.count(),
            "requests": DataRequest.objects.filter(institution=institution).count() if institution else DataRequest.objects.count(),
            "audit": AuditEvent.objects.filter(institution=institution).count() if institution else AuditEvent.objects.count(),
        },
        "db_engine": connection.vendor,
        "ai_provider": getattr(institution, "ai_provider", "mock") if institution else "mock",
        "ai_model": getattr(institution, "ai_model", "") if institution else "",
        "pwa": {
            "manifest": (Path(settings.STATICFILES_DIRS[0]) / "manifest.json").exists(),
            "service_worker": (Path(settings.STATICFILES_DIRS[0]) / "sw.js").exists(),
        },
        "last_backup": backups[0].name if backups else None,
    }
    return render(request, "governance/health.html", context)
