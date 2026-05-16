from django.urls import path
from . import views

urlpatterns = [
    path('', views.score_list, name='score_list'),
    path('add/', views.score_add, name='score_add'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('rounds/', views.round_list, name='round_list'),
    path('rounds/create/', views.round_create, name='round_create'),
]
