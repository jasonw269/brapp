import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import ChatMessage, ChatRead

PAGE_SIZE = 60   # messages to load initially
POLL_SIZE = 50   # max messages returned per poll


def _unread_count(user):
    """Return number of messages the user hasn't read yet."""
    try:
        cr = user.chat_read
        last_id = cr.last_read_id or 0
    except ChatRead.DoesNotExist:
        last_id = 0
    return ChatMessage.objects.filter(pk__gt=last_id).exclude(author=user).count()


@login_required
def chat_view(request):
    messages_qs = ChatMessage.objects.select_related(
        'author', 'author__profile'
    ).order_by('-created_at')[:PAGE_SIZE]
    messages_list = list(reversed(messages_qs))

    # Mark all current messages as read
    latest = ChatMessage.objects.order_by('-pk').first()
    if latest:
        ChatRead.objects.update_or_create(
            user=request.user,
            defaults={'last_read': latest},
        )

    return render(request, 'chat/chat.html', {
        'messages': messages_list,
        'latest_id': latest.pk if latest else 0,
    })


@login_required
def poll_messages(request):
    """
    Long-poll endpoint: returns messages newer than ?after=<id>.
    Also marks them as read.
    """
    after_id = int(request.GET.get('after', 0))
    new_msgs = ChatMessage.objects.filter(
        pk__gt=after_id
    ).select_related('author', 'author__profile').order_by('created_at')[:POLL_SIZE]

    data = []
    latest_id = after_id
    for m in new_msgs:
        latest_id = m.pk
        try:
            photo_url = m.author.profile.photo.url if m.author.profile.photo else None
        except Exception:
            photo_url = None

        initials = ''
        if m.author:
            fn = m.author.first_name or ''
            ln = m.author.last_name or ''
            initials = (fn[:1] + ln[:1]).upper() or m.author.username[:2].upper()

        data.append({
            'id':       m.pk,
            'author':   m.author.get_full_name() if m.author else 'Unknown',
            'username': m.author.username if m.author else '',
            'initials': initials,
            'photo':    photo_url,
            'body':     m.body,
            'time':     m.created_at.strftime('%H:%M'),
            'date':     m.created_at.strftime('%d %b %Y'),
            'is_me':    m.author_id == request.user.pk,
        })

    # Mark as read
    if latest_id > after_id:
        latest_msg = ChatMessage.objects.get(pk=latest_id)
        ChatRead.objects.update_or_create(
            user=request.user,
            defaults={'last_read': latest_msg},
        )

    return JsonResponse({'messages': data, 'latest_id': latest_id})


@login_required
@require_POST
def send_message(request):
    try:
        payload = json.loads(request.body)
        body = payload.get('body', '').strip()
    except (json.JSONDecodeError, AttributeError):
        body = request.POST.get('body', '').strip()

    if not body:
        return JsonResponse({'error': 'Empty message'}, status=400)
    if len(body) > 1000:
        return JsonResponse({'error': 'Message too long (max 1000 characters)'}, status=400)

    msg = ChatMessage.objects.create(author=request.user, body=body)

    try:
        photo_url = request.user.profile.photo.url if request.user.profile.photo else None
    except Exception:
        photo_url = None

    fn = request.user.first_name or ''
    ln = request.user.last_name or ''
    initials = (fn[:1] + ln[:1]).upper() or request.user.username[:2].upper()

    # Mark own message as read immediately
    ChatRead.objects.update_or_create(
        user=request.user,
        defaults={'last_read': msg},
    )

    return JsonResponse({
        'id':       msg.pk,
        'author':   request.user.get_full_name() or request.user.username,
        'username': request.user.username,
        'initials': initials,
        'photo':    photo_url,
        'body':     msg.body,
        'time':     msg.created_at.strftime('%H:%M'),
        'date':     msg.created_at.strftime('%d %b %Y'),
        'is_me':    True,
    })


@login_required
def unread_count(request):
    """JSON endpoint for badge polling."""
    return JsonResponse({'count': _unread_count(request.user)})
