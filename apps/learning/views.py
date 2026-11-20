from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message, MessageSource
from .serializers import ConversationSerializer, ChatInputSerializer, MessageSerializer
from .retrieval import retrieve_context
from apps.ai_gateway.services import AIGateway
from apps.audit.models import AuditEvent
from apps.institutions.models import Membership
@login_required(login_url="/accounts/login/")
def companion_page(request):
    return render(request, "learning/companion.html")
class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        membership = Membership.objects.filter(user=self.request.user, is_active=True).first()
        if not membership:
            return Conversation.objects.none()
        return Conversation.objects.filter(institution=membership.institution, user=self.request.user)
    def perform_create(self, serializer):
        membership = Membership.objects.filter(user=self.request.user, is_active=True).first()
        if not membership:
            raise Exception("User must be a member of an institution to start a conversation.")
        serializer.save(user=self.request.user, institution=membership.institution)
    @action(detail=True, methods=["post"], url_path="chat")
    def chat(self, request, pk=None):
        conversation = self.get_object()
        serializer = ChatInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prompt = serializer.validated_data["prompt"]
        Message.objects.create(conversation=conversation, role=Message.Role.USER, content=prompt)
        chunks = retrieve_context(prompt, conversation.institution_id, top_k=5)
        gateway = AIGateway(institution=conversation.institution)
        context_text = "\n\n".join(c.chunk_text for c in chunks)
        content = gateway.generate_learning_response(prompt, context_text)
        assistant_message = Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=content,
            model_provider=gateway.provider.provider_name,
        )
        for chunk in chunks:
            MessageSource.objects.create(
                message=assistant_message, resource=chunk.resource, chunk=chunk, relevance_score=1.0)
        AuditEvent.objects.create(
            institution=conversation.institution, actor=request.user,
            action="AI_LEARNING_QUERY", resource_type="Conversation",
            resource_id=str(conversation.id),
            metadata={"provider": gateway.provider.provider_name, "chunks_used": len(chunks)})
        return Response(MessageSerializer(assistant_message).data, status=status.HTTP_201_CREATED)
