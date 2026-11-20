from rest_framework import serializers
from .models import TeachingArtifact
class TeachingArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeachingArtifact
        fields = ['id', 'artifact_type', 'topic', 'grade_level', 'content', 'created_at']
        read_only_fields = ['id', 'content', 'created_at']
class ArtifactGenerationInputSerializer(serializers.Serializer):
    artifact_type = serializers.ChoiceField(choices=TeachingArtifact.ArtifactType.choices)
    topic = serializers.CharField(max_length=255)
    grade_level = serializers.CharField(max_length=50)
    curriculum = serializers.CharField(max_length=100, default="CBC/CBE")
