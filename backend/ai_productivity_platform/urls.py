"""
URL configuration for AI Productivity Platform.

The `urlpatterns` list routes URLs to views.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='dashboard/main.html'), name='dashboard'),

    # API endpoints
    path('api/auth/', include('apps.users.urls')),
    path('api/notes/', include('apps.notes.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/ai/', include('apps.ai_engine.urls')),
    path('api/core/', include('apps.core.urls')),

    # Authentication
    path('auth/', include('django.contrib.auth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)