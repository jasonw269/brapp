from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Membership, MembershipLevel
from .forms import MembershipForm
from accounts.models import User

# Roles that can manage membership records
MEMBERSHIP_ROLES = ('Chair', 'Treasurer', 'Secretary', 'Member')


def can_manage_memberships(user):
    return user.is_admin or user.committee_role in MEMBERSHIP_ROLES


@login_required
def membership_list(request):
    if can_manage_memberships(request.user):
        memberships = Membership.objects.select_related('user', 'level').order_by('-end_date')
    else:
        memberships = Membership.objects.filter(user=request.user).select_related('level').order_by('-end_date')
    return render(request, 'memberships/list.html', {'memberships': memberships, 'can_manage': can_manage_memberships(request.user)})


@login_required
def membership_create(request, user_id=None):
    if not can_manage_memberships(request.user):
        messages.error(request, 'You do not have permission to create memberships.')
        return redirect('membership_list')

    if user_id:
        target_user = get_object_or_404(User, pk=user_id)
    else:
        # If no user specified, let them pick from the form
        target_user = None

    if request.method == 'POST':
        # Allow picking user from POST if not pre-set
        if not target_user:
            uid = request.POST.get('user_id')
            target_user = get_object_or_404(User, pk=uid) if uid else request.user

        form = MembershipForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.user = target_user
            membership.created_by = request.user
            membership.save()
            messages.success(request, f'Membership created for {target_user}.')
            return redirect('member_profile', user_id=target_user.pk)
    else:
        form = MembershipForm()

    # Provide list of members if no target specified
    members = None
    if not target_user:
        members = User.objects.filter(role__in=['member', 'admin']).order_by('first_name', 'last_name')

    return render(request, 'memberships/form.html', {
        'form': form,
        'target_user': target_user,
        'members': members,
        'action': 'Create',
    })


@login_required
def membership_edit(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    if not can_manage_memberships(request.user):
        messages.error(request, 'Access denied.')
        return redirect('membership_list')

    if request.method == 'POST':
        form = MembershipForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membership updated.')
            return redirect('member_profile', user_id=membership.user.pk)
    else:
        form = MembershipForm(instance=membership)

    return render(request, 'memberships/form.html', {
        'form': form,
        'target_user': membership.user,
        'action': 'Edit',
    })
