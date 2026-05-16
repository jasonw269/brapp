from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about, name='about'),
    path('about/edit/', views.about_edit, name='about_edit'),
    path('contact/', views.contact, name='contact'),
    path('contact/edit/', views.contact_edit, name='contact_edit'),
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/upload/', views.gallery_upload, name='gallery_upload'),
    path('gallery/delete/<int:pk>/', views.gallery_delete, name='gallery_delete'),
]
