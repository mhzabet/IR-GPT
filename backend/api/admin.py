from django.contrib import admin
from .models import Conversation, Messages, MessageArchived

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username')
    list_filter = ('created_at',)

@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'status', 'position', 'created_at', 'updated_at')
    search_fields = ('content', 'conversation__title', 'role')
    list_filter = ('role', 'status', 'created_at')

@admin.register(MessageArchived)
class MessageArchivedAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'status', 'position', 'archived_at', 'created_at', 'updated_at')
    search_fields = ('content', 'conversation__title', 'role')
    list_filter = ('role', 'status', 'archived_at')
