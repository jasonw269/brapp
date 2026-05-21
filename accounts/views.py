from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Profile
from .forms import (LoginForm, ProfileForm, ProfileMembershipForm,
                    UserRoleForm, UserCreateForm, PasswordChangeAdminForm)

MEMBERSHIP_ROLES = ('Chair', 'Treasurer', 'Secretary', 'Member')


def _can_edit_join_date(user):
    return user.is_admin or user.committee_role in MEMBERSHIP_ROLES


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request, user_id=None):
    target_user = get_object_or_404(User, pk=user_id) if user_id else request.user
    profile, _ = Profile.objects.get_or_create(
        user=target_user,
        defaults={'full_name': target_user.get_full_name() or target_user.username}
    )
    return render(request, 'accounts/profile.html', {
        'profile_user': target_user,
        'profile': profile,
        'can_edit_join_date': _can_edit_join_date(request.user),
    })


@login_required
def profile_edit(request, user_id=None):
    """Edit own profile, or another user's profile if admin/membership officer."""
    if user_id and _can_edit_join_date(request.user):
        target_user = get_object_or_404(User, pk=user_id)
    else:
        target_user = request.user

    profile, _ = Profile.objects.get_or_create(
        user=target_user,
        defaults={'full_name': target_user.get_full_name() or target_user.username}
    )

    # Membership officers get the extended form with date_joined_club
    FormClass = ProfileMembershipForm if _can_edit_join_date(request.user) else ProfileForm

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            if user_id:
                return redirect('member_profile', user_id=target_user.pk)
            return redirect('profile')
    else:
        form = FormClass(instance=profile)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'target_user': target_user,
        'editing_other': target_user != request.user,
        'can_edit_join_date': _can_edit_join_date(request.user),
    })


@login_required
def member_list(request):
    if not request.user.is_member:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    members = User.objects.filter(
        role__in=['member', 'admin']
    ).select_related('profile').order_by('first_name', 'last_name')
    return render(request, 'accounts/member_list.html', {'members': members})


@login_required
def user_list_admin(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    users = User.objects.select_related('profile').order_by('first_name', 'last_name')
    return render(request, 'accounts/user_list_admin.html', {'users': users})


@login_required
def user_create(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('user_list_admin')
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.committee_role and user.role == 'guest':
                user.role = 'member'
            user.save()
            Profile.objects.create(
                user=user,
                full_name=user.get_full_name() or user.username
            )
            messages.success(request, f'User {user} created successfully.')
            return redirect('user_role_edit', user_id=user.pk)
    else:
        form = UserCreateForm()
    return render(request, 'accounts/user_create.html', {'form': form})


@login_required
def user_role_edit(request, user_id):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('member_list')
    target_user = get_object_or_404(User, pk=user_id)
    if target_user == request.user and not target_user.is_superuser:
        messages.warning(request, 'You cannot change your own role.')
        return redirect('member_profile', user_id=user_id)
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=target_user)
        if form.is_valid():
            user = form.save(commit=False)
            if user.committee_role and user.role == 'guest':
                user.role = 'member'
            if user.role in ('guest', 'course_guest'):
                user.committee_role = None
            user.save()
            messages.success(request, f'Roles updated for {target_user}.')
            return redirect('member_profile', user_id=user_id)
    else:
        form = UserRoleForm(instance=target_user)
    return render(request, 'accounts/user_role_edit.html', {
        'form': form, 'target_user': target_user,
    })


@login_required
def user_password_change(request, user_id):
    """Admin-only: change any user's password."""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = PasswordChangeAdminForm(request.POST)
        if form.is_valid():
            target_user.set_password(form.cleaned_data['new_password1'])
            target_user.save()
            messages.success(request, f'Password changed for {target_user}.')
            return redirect('member_profile', user_id=user_id)
    else:
        form = PasswordChangeAdminForm()
    return render(request, 'accounts/password_change.html', {
        'form': form, 'target_user': target_user,
    })
