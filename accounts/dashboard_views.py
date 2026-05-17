from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from events.models import Event, EventAttendance
from memberships.models import Membership
from badges.models import MemberBadge


@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()
    now = timezone.now()

    context = {'user': user, 'today': today}

    if user.is_member:
        # Membership status
        active_membership = Membership.objects.filter(
            user=user, start_date__lte=today, end_date__gte=today
        ).select_related('level').first()
        context['active_membership'] = active_membership

        # Events happening today (any event whose date is today)
        todays_events = Event.objects.filter(
            start_date__date=today
        ).order_by('start_date')
        context['todays_events'] = todays_events

        # Upcoming events (strictly future, not today)
        upcoming_internal = Event.objects.filter(
            event_type='internal', start_date__date__gt=today
        ).order_by('start_date')[:3]
        upcoming_external = Event.objects.filter(
            event_type='external', start_date__date__gt=today
        ).order_by('start_date')[:3]
        context['upcoming_internal'] = upcoming_internal
        context['upcoming_external'] = upcoming_external

        # Events the member is attending (upcoming, including today)
        attending_events = Event.objects.filter(
            attendances__user=user, start_date__gte=now
        ).order_by('start_date')[:5]
        context['attending_events'] = attending_events

        # Recent badges
        recent_badges = MemberBadge.objects.filter(
            user=user
        ).select_related('badge').order_by('-awarded_at')[:5]
        context['recent_badges'] = recent_badges

        # Check-in reminders: events today that user is attending and hasn't checked in
        checkin_events = EventAttendance.objects.filter(
            user=user,
            checked_in=False,
            event__start_date__date=today
        ).select_related('event')
        context['checkin_events'] = checkin_events

    return render(request, 'dashboard/dashboard.html', context)
