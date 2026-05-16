from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Profile
from .forms import LoginForm, ProfileForm, UserRoleForm


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
    })


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={'full_name': request.user.get_full_name() or request.user.username}
    )
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def member_list(request):
    if not request.user.is_member:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    members = User.objects.filter(role__in=['member', 'admin']).select_related('profile').order_by('first_name', 'last_name')
    return render(request, 'accounts/member_list.html', {'members': members})


@login_required
def user_role_edit(request, user_id):
    """Admin-only: edit a user's role and committee role."""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('member_list')

    target_user = get_object_or_404(User, pk=user_id)

    # Prevent admins from locking themselves out
    if target_user == request.user and not target_user.is_superuser:
        messages.warning(request, 'You cannot change your own role.')
        return redirect('member_profile', user_id=user_id)

    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=target_user)
        if form.is_valid():
            user = form.save(commit=False)
            # If committee_role is set, ensure the user is at least a member
            if user.committee_role and user.role == 'guest':
                user.role = 'member'
            # Clear committee_role if user is no longer a member
            if user.role in ('guest', 'course_guest'):
                user.committee_role = None
            user.save()
            messages.success(request, f'Roles updated for {target_user}.')
            return redirect('member_profile', user_id=user_id)
    else:
        form = UserRoleForm(instance=target_user)

    return render(request, 'accounts/user_role_edit.html', {
        'form': form,
        'target_user': target_user,
    })


@login_required
def user_list_admin(request):
    """Admin view of all users with role management."""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    users = User.objects.select_related('profile').order_by('first_name', 'last_name')
    return render(request, 'accounts/user_list_admin.html', {'users': users})
