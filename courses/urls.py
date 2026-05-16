from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:pk>/apply/', views.course_apply, name='course_apply'),
    path('applied/', views.course_applied, name='course_applied'),
    path('manage/', views.course_manage, name='course_manage'),
    path('create/', views.course_create, name='course_create'),
    path('<int:pk>/applications/', views.course_applications, name='course_applications'),
    path('application/<int:pk>/update/', views.application_update, name='application_update'),
]
