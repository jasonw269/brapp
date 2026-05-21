from .views import _unread_count


def chat_unread(request):
    """Inject unread chat count into every template context."""
    if request.user.is_authenticated and request.user.is_member:
        return {'chat_unread_count': _unread_count(request.user)}
    return {'chat_unread_count': 0}
