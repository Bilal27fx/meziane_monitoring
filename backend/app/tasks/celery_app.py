"""
celery_app.py - Configuration Celery

Description:
Instance Celery centrale avec broker Redis.
Utilisée par tous les modules de tasks.

Dépendances:
- celery
- redis (broker + backend)
- config.settings

Utilisé par:
- tasks/banking_tasks.py
- tasks/quittance_tasks.py
"""

from celery import Celery
from celery.schedules import crontab
from app.config import settings
from app.models import load_all_models

load_all_models()

celery_app = Celery(
    "meziane_monitoring",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.banking_tasks",
        "app.tasks.quittance_tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Paris",
    enable_utc=True,
    task_track_started=True,
    beat_schedule={
        "generate-quittances-monthly": {
            "task": "app.tasks.quittance_tasks.generate_quittances_task",
            "schedule": crontab(hour=8, minute=0, day_of_month=1),
        },
        "send-alerte-impayes-weekly": {
            "task": "app.tasks.quittance_tasks.send_alerte_impayes_task",
            "schedule": crontab(hour=9, minute=0, day_of_week=1),
        },
    }
)
