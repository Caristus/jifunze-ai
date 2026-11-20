from rest_framework import serializers
from .models import Conversation, Message, MessageSource
class MessageSourceSerializer(serializers.ModelSerializer):
    resource_title = serializers.CharField(source="resource.title", read_only=True)
    chunk_excerpt = serializers.CharField(source="chunk.chunk_text", read_only=True)
    class Meta:
        model = MessageSource
        fields = ["id", "resource_title", "chunk_excerpt", "relevance_score"]
class MessageSerializer(serializers.ModelSerializer):
    sources = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ["id", "role", "content", "model_provider", "sources", "created_at"]
    def get_sources(self, obj):
        return MessageSourceSerializer(apps.learning.models.MessageSource.objects.filter(message=obj).select_related("resource", "chunk")[:5], many=True).data
class ChatInputSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=2000)
class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = Conversation
        fields = ["id", "title", "institution", "user", "messages", "created_at", "updated_at"]
        read_only_fields = ["id", "institution", "user", "created_at", "updated_at"]




