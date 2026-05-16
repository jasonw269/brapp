from django.urls import path
from . import views

urlpatterns = [
    path('', views.membership_list, name='membership_list'),
    path('create/', views.membership_create, name='membership_create'),
    path('create/<int:user_id>/', views.membership_create, name='membership_create_for'),
    path('edit/<int:pk>/', views.membership_edit, name='membership_edit'),
]
