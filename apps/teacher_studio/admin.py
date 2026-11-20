from django.contrib import admin
from .models import TeachingArtifact
@admin.register(TeachingArtifact)
class TeachingArtifactAdmin(admin.ModelAdmin):
    list_display = ("topic", "artifact_type", "institution", "created_by", "created_at")
    list_filter = ("artifact_type", "institution")
    search_fields = ("topic", "content")
