from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Badge, MemberBadge
from .forms import BadgeForm, AwardBadgeForm
from accounts.models import User


@login_required
def badge_list(request):
    badges = Badge.objects.all()
    return render(request, 'badges/list.html', {'badges': badges})


@login_required
def badge_create(request):
    if not (request.user.is_admin or request.user.committee_role == 'Records'):
        messages.error(request, 'Access denied.')
        return redirect('badge_list')
    if request.method == 'POST':
        form = BadgeForm(request.POST, request.FILES)
        if form.is_valid():
            badge = form.save(commit=False)
            badge.created_by = request.user
            badge.save()
            messages.success(request, 'Badge created.')
            return redirect('badge_list')
    else:
        form = BadgeForm()
    return render(request, 'badges/form.html', {'form': form, 'action': 'Create Badge'})


@login_required
def award_badge(request, user_id):
    if not (request.user.is_admin or request.user.committee_role == 'Records'):
        messages.error(request, 'Access denied.')
        return redirect('badge_list')
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = AwardBadgeForm(request.POST)
        if form.is_valid():
            badge = form.cleaned_data['badge']
            notes = form.cleaned_data.get('notes', '')
            mb, created = MemberBadge.objects.get_or_create(badge=badge, user=target_user, defaults={'awarded_by': request.user, 'notes': notes})
            if created:
                messages.success(request, f'Badge "{badge}" awarded to {target_user}.')
            else:
                messages.info(request, f'{target_user} already has this badge.')
            return redirect('member_profile', user_id=user_id)
    else:
        form = AwardBadgeForm()
    return render(request, 'badges/award.html', {'form': form, 'target_user': target_user})
