from django.db import models
from django.conf import settings


class ChatMessage(models.Model):
    author    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                  null=True, related_name='chat_messages')
    body      = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} @ {self.created_at:%H:%M}: {self.body[:40]}'


class ChatRead(models.Model):
    """Tracks the last message each user has read."""
    user        = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       related_name='chat_read')
    last_read   = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL,
                                     null=True, blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} read up to #{self.last_read_id}'
