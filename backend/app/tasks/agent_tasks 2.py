"""
agent_tasks.py - Tasks Celery agents IA

Description:
Task pour lancement périodique de l'agent prospection immobilier.
Tourne quotidiennement à 6h via Celery Beat.

Dépendances:
- celery_app
- agents.agent_prospection
- utils.db

Utilisé par:
- beat_schedule (quotidien 6h)
- api.opportunite_routes (déclenchement manuel)
"""

from app.tasks.celery_app import celery_app
from app.utils.db import SessionLocal
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


@celery_app.task(name="app.tasks.agent_tasks.run_prospection_agent_task", bind=True, max_retries=1)
def run_prospection_agent_task(self):
    """Lance l'agent prospection immobilier — job quotidien"""
    from app.agents.agent_prospection import AgentProspection

    logger.info("Démarrage run_prospection_agent_task")

    db = SessionLocal()
    try:
        agent = AgentProspection(db)
        result = agent.run()
        logger.info(f"run_prospection_agent_task terminé: {result}")
        return result

    except Exception as exc:
        logger.error(f"run_prospection_agent_task échoué: {exc}")
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()
