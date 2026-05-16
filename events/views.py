from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, EventPollOption, EventPollVote, EventAttendance, Location
from .forms import EventForm, PollOptionFormSet


@login_required
def event_list(request):
    now = timezone.now()
    upcoming = Event.objects.filter(start_date__gte=now).order_by('start_date')
    past = Event.objects.filter(start_date__lt=now).order_by('-start_date')[:10]
    return render(request, 'events/list.html', {'upcoming': upcoming, 'past': past})


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_attendance = None
    if request.user.is_member:
        user_attendance = EventAttendance.objects.filter(event=event, user=request.user).first()
    attendees = EventAttendance.objects.filter(event=event).select_related('user')
    poll_options = event.poll_options.all()
    user_votes = []
    if request.user.is_authenticated:
        user_votes = list(EventPollVote.objects.filter(option__event=event, user=request.user).values_list('option_id', flat=True))
    return render(request, 'events/detail.html', {
        'event': event,
        'user_attendance': user_attendance,
        'attendees': attendees,
        'poll_options': poll_options,
        'user_votes': user_votes,
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
            # Save poll options
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
    event = get_object_or_404(Event, pk=pk)
    attendance = get_object_or_404(EventAttendance, event=event, user=request.user)
    attendance.checked_in = True
    attendance.checked_in_at = timezone.now()
    attendance.save()
    messages.success(request, f'Checked in to {event.title}!')
    return redirect('dashboard')


@login_required
def poll_vote(request, event_pk, option_pk):
    event = get_object_or_404(Event, pk=event_pk)
    option = get_object_or_404(EventPollOption, pk=option_pk, event=event)
    vote, created = EventPollVote.objects.get_or_create(option=option, user=request.user)
    if not created:
        vote.delete()
    return redirect('event_detail', pk=event_pk)
