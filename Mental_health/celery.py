


from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mental_health.settings')

app = Celery('Mental_health')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')


# Explicitly register tasks
# app.autodiscover_tasks(lambda: ['room', 'reviews', 'booking', 'payment', 'analytics'])
app.autodiscover_tasks()

# Optional: Define a debug task
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
app.conf.broker_url = "redis://localhost:6378/0"


app.conf.beat_schedule = {
    'push-notification-every-midnight': {
        'task': 'daily_checking.tasks.push_notification', 
        # 'schedule': crontab(hour=0, minute=0), 
        'schedule': timedelta(minutes=1), 
    },
}