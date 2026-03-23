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
- tasks/agent_tasks.py
- tasks/quittance_tasks.py
"""

from celery import Celery
from app.config import settings

celery_app = Celery(
    "meziane_monitoring",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.banking_tasks",
        "app.tasks.agent_tasks",
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
        # Agent prospection : tous les jours à 6h
        "run-prospection-agent-daily": {
            "task": "app.tasks.agent_tasks.run_prospection_agent_task",
            "schedule": "0 6 * * *",
        },
        # Génération quittances : 1er du mois à 8h
        "generate-quittances-monthly": {
            "task": "app.tasks.quittance_tasks.generate_quittances_task",
            "schedule": "0 8 1 * *",
        },
        # Alertes impayés : tous les lundis à 9h
        "send-alerte-impayes-weekly": {
            "task": "app.tasks.quittance_tasks.send_alerte_impayes_task",
            "schedule": "0 9 * * 1",
        },
    }
)
