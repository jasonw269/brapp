from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<int:user_id>/', views.profile_view, name='member_profile'),
    path('members/', views.member_list, name='member_list'),
    path('users/', views.user_list_admin, name='user_list_admin'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/roles/', views.user_role_edit, name='user_role_edit'),
]
