from rest_framework import serializers
from .models import TeachingArtifact
class TeachingArtifactSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    class Meta:
        model = TeachingArtifact
        fields = ["id", "artifact_type", "topic", "grade_level", "curriculum", "content",
                  "created_by_name", "created_at"]
        read_only_fields = ["id", "created_by_name", "created_at"]
class ArtifactGenerationInputSerializer(serializers.Serializer):
    artifact_type = serializers.ChoiceField(choices=TeachingArtifact.ArtifactType.choices)
    topic = serializers.CharField(max_length=255)
    grade_level = serializers.CharField(max_length=50, required=False, allow_blank=True)
    curriculum = serializers.CharField(max_length=100, required=False, default="CBC/CBE")
