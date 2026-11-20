from django.contrib import admin
from .models import Conversation, Message, MessageSource
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("created_at",)
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "institution", "updated_at")
    list_filter = ("institution", "user__role")
    search_fields = ("title", "user__username")
    inlines = [MessageInline]
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "role", "model_provider", "created_at")
    list_filter = ("role", "model_provider")
@admin.register(MessageSource)
class MessageSourceAdmin(admin.ModelAdmin):
    list_display = ("message", "resource")
