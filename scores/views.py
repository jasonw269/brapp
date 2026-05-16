from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max
from .models import Score, Round
from .forms import ScoreForm, RoundForm
from accounts.models import User


@login_required
def score_list(request):
    user_id = request.GET.get('user')
    if user_id and request.user.is_admin:
        target_user = get_object_or_404(User, pk=user_id)
    else:
        target_user = request.user
    scores = Score.objects.filter(user=target_user).select_related('round').order_by('-date_shot')
    return render(request, 'scores/list.html', {'scores': scores, 'target_user': target_user})


@login_required
def score_add(request):
    if not request.user.is_member:
        messages.error(request, 'Only members can add scores.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = ScoreForm(request.POST)
        if form.is_valid():
            score = form.save(commit=False)
            score.user = request.user
            score.save()
            messages.success(request, 'Score added successfully.')
            return redirect('score_list')
    else:
        form = ScoreForm()
    return render(request, 'scores/form.html', {'form': form, 'action': 'Add Score'})


@login_required
def leaderboard(request):
    rounds = Round.objects.filter(is_active=True)
    selected_round_id = request.GET.get('round')
    selected_bow = request.GET.get('bow', '')
    leaderboard_data = []
    selected_round = None

    if selected_round_id:
        selected_round = get_object_or_404(Round, pk=selected_round_id)
        qs = Score.objects.filter(round=selected_round, is_personal_best=True).select_related('user', 'user__profile')
        if selected_bow:
            qs = qs.filter(bow_type=selected_bow)
        leaderboard_data = qs.order_by('-score')

    bow_choices = Score.BOW_CHOICES
    return render(request, 'scores/leaderboard.html', {
        'rounds': rounds,
        'selected_round': selected_round,
        'selected_bow': selected_bow,
        'leaderboard_data': leaderboard_data,
        'bow_choices': bow_choices,
    })


@login_required
def round_list(request):
    rounds = Round.objects.all()
    return render(request, 'scores/round_list.html', {'rounds': rounds})


@login_required
def round_create(request):
    if not (request.user.is_committee or request.user.is_admin):
        messages.error(request, 'Only committee members can create rounds.')
        return redirect('round_list')
    if request.method == 'POST':
        form = RoundForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.created_by = request.user
            r.save()
            messages.success(request, 'Round created.')
            return redirect('round_list')
    else:
        form = RoundForm()
    return render(request, 'scores/round_form.html', {'form': form, 'action': 'Create'})
