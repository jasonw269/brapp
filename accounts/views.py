from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import User, Profile
from .forms import LoginForm, UserRegistrationForm, ProfileForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request, user_id=None):
    if user_id:
        target_user = get_object_or_404(User, pk=user_id)
    else:
        target_user = request.user
    profile, _ = Profile.objects.get_or_create(user=target_user, defaults={'full_name': target_user.get_full_name() or target_user.username})
    return render(request, 'accounts/profile.html', {'profile_user': target_user, 'profile': profile})


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'full_name': request.user.get_full_name() or request.user.username})
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
    members = User.objects.filter(role__in=['member', 'admin']).select_related('profile').order_by('first_name')
    return render(request, 'accounts/member_list.html', {'members': members})
