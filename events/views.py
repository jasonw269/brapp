from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, EventPollOption, EventPollVote, EventAttendance, Location
from .forms import EventForm
from accounts.models import User


def _checkin_allowed(event):
    """Check-in is open from event creation until midnight on the day of the event."""
    now = timezone.now()
    event_date = event.start_date.date()
    # Midnight at end of the event's day (i.e. start of next day)
    midnight = timezone.make_aware(
        timezone.datetime(event_date.year, event_date.month, event_date.day, 23, 59, 59)
    )
    return now <= midnight


@login_required
def event_list(request):
    now = timezone.now()
    upcoming = Event.objects.filter(start_date__gte=now).order_by('start_date')
    past = Event.objects.filter(start_date__lt=now).order_by('-start_date')[:10]
    return render(request, 'events/list.html', {'upcoming': upcoming, 'past': past})


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    now = timezone.now()
    today = now.date()

    user_attendance = None
    if request.user.is_member:
        user_attendance = EventAttendance.objects.filter(
            event=event, user=request.user
        ).first()

    # All attendees with their poll votes for this event
    attendees = EventAttendance.objects.filter(
        event=event
    ).select_related('user', 'user__profile').order_by('user__first_name')

    poll_options = event.poll_options.all()

    # Current user's votes
    user_votes = []
    if request.user.is_authenticated:
        user_votes = list(
            EventPollVote.objects.filter(
                option__event=event, user=request.user
            ).values_list('option_id', flat=True)
        )

    # Build per-attendee vote map: {attendance_id: [option_text, ...]}
    attendee_votes = {}
    if poll_options.exists():
        all_votes = EventPollVote.objects.filter(
            option__event=event
        ).select_related('option').values('user_id', 'option__text')
        for v in all_votes:
            attendee_votes.setdefault(v['user_id'], []).append(v['option__text'])

    checkin_open = _checkin_allowed(event)
    is_today = event.start_date.date() == today

    # Total votes per option for the poll bar widths
    total_votes = sum(o.votes.count() for o in poll_options) or 1

    from accounts.models import User as UserModel
    all_members = UserModel.objects.filter(
        role__in=['member', 'admin']
    ).order_by('first_name', 'last_name') if (
        request.user.is_admin or request.user.is_committee
    ) else []

    return render(request, 'events/detail.html', {
        'event': event,
        'user_attendance': user_attendance,
        'attendees': attendees,
        'poll_options': poll_options,
        'user_votes': user_votes,
        'attendee_votes': attendee_votes,
        'checkin_open': checkin_open,
        'is_today': is_today,
        'total_votes': total_votes,
        'all_members': all_members,
    })


@login_required
def event_create(request):
    if not request.user.is_committee and not request.user.is_admin:
        messages.error(request, 'Only committee members can create events.')
        return redirect('event_list')
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            options = request.POST.getlist('poll_option')
            for i, opt in enumerate(options):
                if opt.strip():
                    EventPollOption.objects.create(event=event, text=opt.strip(), order=i)
            messages.success(request, 'Event created.')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
    locations = Location.objects.filter(is_active=True)
    return render(request, 'events/form.html', {'form': form, 'locations': locations, 'action': 'Create'})


@login_required
def event_attend(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not request.user.is_member:
        messages.error(request, 'Only members can sign up for events.')
        return redirect('event_detail', pk=pk)
    attendance, created = EventAttendance.objects.get_or_create(event=event, user=request.user)
    if created:
        messages.success(request, f'You are now registered for {event.title}.')
    else:
        attendance.delete()
        messages.info(request, f'You have withdrawn from {event.title}.')
    return redirect('event_detail', pk=pk)


@login_required
def event_checkin(request, pk):
    """Check in the current user (or another user if admin/committee).
    Committee members can check in any member even if they haven't registered to attend.
    """
    event = get_object_or_404(Event, pk=pk)

    if not _checkin_allowed(event):
        messages.error(request, 'Check-in is no longer available for this event.')
        return redirect('event_detail', pk=pk)

    # Admin/committee checking in another user
    target_user_id = request.POST.get('checkin_user_id') if request.method == 'POST' else None
    if target_user_id and (request.user.is_admin or request.user.is_committee):
        target_user = get_object_or_404(User, pk=target_user_id)
        # Create attendance record if it doesn't exist (walk-in)
        attendance, created = EventAttendance.objects.get_or_create(
            event=event, user=target_user
        )
    else:
        target_user = request.user
        attendance = get_object_or_404(EventAttendance, event=event, user=target_user)

    if not attendance.checked_in:
        attendance.checked_in = True
        attendance.checked_in_at = timezone.now()
        attendance.save()
        name = target_user.get_full_name() or target_user.username
        if target_user == request.user:
            messages.success(request, f'Checked in to {event.title}!')
        else:
            messages.success(request, f'{name} checked in{"  (walk-in)" if created else ""}.')
    else:
        name = target_user.get_full_name() or target_user.username
        messages.info(request, f'{name} is already checked in.')

    if target_user != request.user:
        return redirect('event_detail', pk=pk)
    return redirect('dashboard')


@login_required
def poll_vote(request, event_pk, option_pk):
    event = get_object_or_404(Event, pk=event_pk)
    option = get_object_or_404(EventPollOption, pk=option_pk, event=event)
    vote, created = EventPollVote.objects.get_or_create(option=option, user=request.user)
    if not created:
        vote.delete()
    return redirect('event_detail', pk=event_pk)
