from django.contrib import admin
from .models import LearningResource, DocumentChunk
@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "institution", "subject", "grade_level", "topic", "status", "created_at")
    list_filter = ("status", "institution", "subject")
    search_fields = ("title", "subject", "topic")
@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("resource", "chunk_index")
    list_filter = ("resource__institution",)
