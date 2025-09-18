"""
Celery configuration for AI Productivity Platform.

This module sets up Celery for handling asynchronous tasks,
particularly for AI API calls and background processing.
"""
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_productivity_platform.settings')

app = Celery('ai_productivity_platform')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'cleanup-expired-tasks': {
        'task': 'apps.core.tasks.cleanup_expired_tasks',
        'schedule': 3600.0,  # Run every hour
    },
    'generate-daily-reports': {
        'task': 'apps.ai_engine.tasks.generate_daily_ai_reports',
        'schedule': 86400.0,  # Run daily
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')