from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Membership, MembershipLevel
from .forms import MembershipForm
from accounts.models import User


@login_required
def membership_list(request):
    if request.user.is_admin or request.user.committee_role == 'Member':
        memberships = Membership.objects.select_related('user', 'level').order_by('-end_date')
        return render(request, 'memberships/list.html', {'memberships': memberships})
    # Show own memberships only
    memberships = Membership.objects.filter(user=request.user).select_related('level').order_by('-end_date')
    return render(request, 'memberships/list.html', {'memberships': memberships})


@login_required
def membership_create(request, user_id=None):
    if not (request.user.is_admin or request.user.committee_role == 'Member'):
        messages.error(request, 'You do not have permission to create memberships.')
        return redirect('membership_list')
    if user_id:
        target_user = get_object_or_404(User, pk=user_id)
    else:
        target_user = request.user
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.user = target_user
            membership.created_by = request.user
            membership.save()
            messages.success(request, 'Membership created.')
            return redirect('membership_list')
    else:
        form = MembershipForm()
    return render(request, 'memberships/form.html', {'form': form, 'target_user': target_user, 'action': 'Create'})


@login_required
def membership_edit(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    if not (request.user.is_admin or request.user.committee_role == 'Member' or membership.user == request.user):
        messages.error(request, 'Access denied.')
        return redirect('membership_list')
    if request.method == 'POST':
        form = MembershipForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membership updated.')
            return redirect('membership_list')
    else:
        form = MembershipForm(instance=membership)
    return render(request, 'memberships/form.html', {'form': form, 'action': 'Edit'})
