from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('create/', views.event_create, name='event_create'),
    path('<int:pk>/attend/', views.event_attend, name='event_attend'),
    path('<int:pk>/checkin/', views.event_checkin, name='event_checkin'),
    path('<int:event_pk>/poll/<int:option_pk>/vote/', views.poll_vote, name='poll_vote'),
]
