from django.urls import path
from . import views

urlpatterns = [
    path('', views.badge_list, name='badge_list'),
    path('create/', views.badge_create, name='badge_create'),
    path('award/<int:user_id>/', views.award_badge, name='award_badge'),
]
