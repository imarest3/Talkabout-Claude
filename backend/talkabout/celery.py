"""
Celery configuration for talkabout project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talkabout.settings')

app = Celery('talkabout')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule
app.conf.beat_schedule = {
    'check-upcoming-events': {
        'task': 'apps.events.tasks.check_upcoming_events',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'start-scheduled-meetings': {
        'task': 'apps.meetings.tasks.start_scheduled_meetings',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
