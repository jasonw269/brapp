from django.urls import path
from . import views

urlpatterns = [
    path('',        views.chat_view,    name='chat'),
    path('poll/',   views.poll_messages, name='chat_poll'),
    path('send/',   views.send_message,  name='chat_send'),
    path('unread/', views.unread_count,  name='chat_unread'),
]
