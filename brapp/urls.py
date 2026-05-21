from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pages import views as page_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', page_views.about, name='home'),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('accounts.dashboard_urls')),
    path('memberships/', include('memberships.urls')),
    path('events/', include('events.urls')),
    path('scores/', include('scores.urls')),
    path('forum/', include('forum.urls')),
    path('badges/', include('badges.urls')),
    path('courses/', include('courses.urls')),
    path('chat/',    include('chat.urls')),
    path('', include('pages.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
