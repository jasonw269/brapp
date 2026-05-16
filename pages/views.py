from django.shortcuts import render
from .models import GalleryImage


def about(request):
    return render(request, 'pages/about.html')


def contact(request):
    return render(request, 'pages/contact.html')


def gallery(request):
    images = GalleryImage.objects.all()
    return render(request, 'pages/gallery.html', {'images': images})
