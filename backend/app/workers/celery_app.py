"""Celery app configuration."""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "creditledger",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Lagos",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
    task_default_queue="default",
    task_routes={
        "app.workers.tasks.send_reminders": {"queue": "reminders"},
        "app.workers.tasks.mark_overdue": {"queue": "maintenance"},
    },
    beat_schedule={
        "mark-overdue-daily": {
            "task": "app.workers.tasks.mark_overdue",
            "schedule": 86400.0,  # daily
        },
        "send-reminders-daily": {
            "task": "app.workers.tasks.send_reminders",
            "schedule": 3600.0,  # hourly
        },
    },
)
