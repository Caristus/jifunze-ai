from rest_framework import serializers
from .models import Conversation, Message, MessageSource
class MessageSourceSerializer(serializers.ModelSerializer):
    resource_title = serializers.CharField(source="resource.title", read_only=True)
    chunk_excerpt = serializers.SerializerMethodField()
    class Meta:
        model = MessageSource
        fields = ["id", "resource_title", "chunk_excerpt", "relevance_score"]
    def get_chunk_excerpt(self, obj):
        return obj.chunk.chunk_text[:220]
class MessageSerializer(serializers.ModelSerializer):
    sources = MessageSourceSerializer(read_only=True, many=True)
    class Meta:
        model = Message
        fields = ["id", "role", "content", "model_provider", "sources", "created_at"]
        read_only_fields = ["id", "role", "model_provider", "created_at"]
class ChatInputSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True)
class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(read_only=True, many=True)
    class Meta:
        model = Conversation
        fields = ["id", "title", "institution", "user", "messages", "created_at", "updated_at"]
        read_only_fields = ["id", "institution", "user", "created_at", "updated_at"]
