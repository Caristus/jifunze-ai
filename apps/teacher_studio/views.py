from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TeachingArtifact
from .serializers import TeachingArtifactSerializer, ArtifactGenerationInputSerializer
from apps.ai_gateway.services import AIGateway
from apps.audit.models import AuditEvent
from apps.institutions.models import Membership
@login_required(login_url="/accounts/login/")
def studio_page(request):
    return render(request, "teacher_studio/studio.html")
class TeachingArtifactViewSet(viewsets.ModelViewSet):
    serializer_class = TeachingArtifactSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        membership = Membership.objects.filter(user=self.request.user, is_active=True).first()
        if not membership:
            return TeachingArtifact.objects.none()
        return TeachingArtifact.objects.filter(institution=membership.institution)
    def perform_create(self, serializer):
        membership = Membership.objects.filter(user=self.request.user, is_active=True).first()
        if not membership:
            raise Exception("User must be a member of an institution.")
        serializer.save(created_by=self.request.user, institution=membership.institution)
    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        serializer = ArtifactGenerationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = Membership.objects.filter(user=request.user, is_active=True).first()
        gateway = AIGateway()
        content = gateway.generate_teacher_artifact(
            artifact_type=serializer.validated_data["artifact_type"],
            topic=serializer.validated_data["topic"],
            grade_level=serializer.validated_data["grade_level"],
            curriculum=serializer.validated_data["curriculum"])
        artifact = TeachingArtifact.objects.create(
            institution=membership.institution, created_by=request.user,
            artifact_type=serializer.validated_data["artifact_type"],
            topic=serializer.validated_data["topic"],
            grade_level=serializer.validated_data["grade_level"], content=content)
        AuditEvent.objects.create(
            institution=membership.institution, actor=request.user,
            action="TEACHER_ARTIFACT_GENERATED", resource_type="TeachingArtifact",
            resource_id=str(artifact.id), metadata={"type": artifact.artifact_type})
        return Response(TeachingArtifactSerializer(artifact).data, status=status.HTTP_201_CREATED)
