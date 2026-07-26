import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("nexus")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "close-stale-open-projects-daily": {
        "task": "apps.projects.tasks.close_stale_open_projects",
        "schedule": crontab(hour=3, minute=0),  
    },
    "purge-expired-otps-hourly": {
        "task": "apps.accounts.tasks.purge_expired_otps",
        "schedule": crontab(minute=0),  
    },
}