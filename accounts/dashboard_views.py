from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from events.models import Event, EventAttendance
from memberships.models import Membership
from badges.models import MemberBadge
from forum.models import Post
from chat.views import _unread_count


@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()
    now = timezone.now()

    context = {'user': user, 'today': today}

    if user.is_member:
        # ── Membership status ──
        active_membership = Membership.objects.filter(
            user=user, start_date__lte=today, end_date__gte=today
        ).select_related('level').first()
        context['active_membership'] = active_membership

        # ── Member since (earliest membership start or date_joined_club) ──
        member_since = None
        try:
            if user.profile.date_joined_club:
                member_since = user.profile.date_joined_club
        except Exception:
            pass

        if not member_since:
            earliest = Membership.objects.filter(user=user).order_by('start_date').first()
            if earliest:
                member_since = earliest.start_date

        context['member_since'] = member_since
        if member_since:
            delta = today - member_since
            years  = delta.days // 365
            months = (delta.days % 365) // 30
            if years > 0:
                context['member_duration'] = f'{years} year{"s" if years != 1 else ""}' + (f', {months} month{"s" if months != 1 else ""}' if months else '')
            elif months > 0:
                context['member_duration'] = f'{months} month{"s" if months != 1 else ""}'
            else:
                context['member_duration'] = f'{delta.days} day{"s" if delta.days != 1 else ""}'

        # ── Membership expiry warning (next 30 days, no future membership) ──
        expiry_warning = None
        if active_membership:
            days_left = (active_membership.end_date - today).days
            if days_left <= 30:
                # Check if a future membership already exists
                future_exists = Membership.objects.filter(
                    user=user, start_date__gt=today
                ).exists()
                if not future_exists:
                    expiry_warning = days_left
        context['expiry_warning'] = expiry_warning

        # ── Events today ──
        todays_events = Event.objects.filter(
            start_date__date=today
        ).order_by('start_date')
        context['todays_events'] = todays_events

        # ── Upcoming events (future only) ──
        upcoming_internal = Event.objects.filter(
            event_type='internal', start_date__date__gt=today
        ).order_by('start_date')[:3]
        upcoming_external = Event.objects.filter(
            event_type='external', start_date__date__gt=today
        ).order_by('start_date')[:3]
        context['upcoming_internal'] = upcoming_internal
        context['upcoming_external'] = upcoming_external

        # ── Events attending (upcoming including today) ──
        attending_events = Event.objects.filter(
            attendances__user=user, start_date__gte=now
        ).order_by('start_date')[:5]
        context['attending_events'] = attending_events

        # ── Recent badges ──
        recent_badges = MemberBadge.objects.filter(
            user=user
        ).select_related('badge').order_by('-awarded_at')[:5]
        context['recent_badges'] = recent_badges

        # ── Check-in reminders ──
        checkin_events = EventAttendance.objects.filter(
            user=user, checked_in=False, event__start_date__date=today
        ).select_related('event')
        context['checkin_events'] = checkin_events

        # ── Latest forum post ──
        latest_post = Post.objects.select_related(
            'topic', 'author', 'author__profile'
        ).order_by('-created_at').first()
        context['latest_post'] = latest_post

        # ── Unread chat messages ──
        context['chat_unread'] = _unread_count(user)

    return render(request, 'dashboard/dashboard.html', context)
