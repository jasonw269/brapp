from django.contrib import admin
from .models import ChatMessage, ChatRead

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['author', 'body', 'created_at']
    list_filter  = ['created_at']
    search_fields = ['author__username', 'body']
    readonly_fields = ['created_at']

admin.site.register(ChatRead)
