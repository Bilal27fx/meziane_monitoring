"""
auction_tasks.py - Tasks Celery auctions

Description:
Tasks Celery du domaine auctions. Cette tranche execute un run d'ingestion
sur payload HTML fourni par le dashboard, avant branchement du fetch reseau.
"""

from app.tasks.celery_app import celery_app
from app.services.auction_ingestion_service import execute_auction_ingestion_run
from app.services.auction_run_log_service import log_agent_run_event
from app.utils.db import SessionLocal
from app.utils.logger import setup_logger
from app.models.agent_run_event import AgentRunEventLevel

logger = setup_logger(__name__)


@celery_app.task(name="app.tasks.auction_tasks.run_auction_ingestion_task", bind=True, max_retries=0)
def run_auction_ingestion_task(self, run_id: int):
    """Execute un run d'ingestion auctions persistant et idempotent."""
    db = SessionLocal()
    try:
        log_agent_run_event(
            db,
            run_id,
            "task_received",
            "Task Celery recue pour le run auctions",
            step="task",
        )
        db.commit()
        result = execute_auction_ingestion_run(db, run_id)
        logger.info(f"run_auction_ingestion_task termine: {result}")
        return result
    except Exception as exc:
        try:
            log_agent_run_event(
                db,
                run_id,
                "task_failed",
                str(exc),
                level=AgentRunEventLevel.ERROR,
                step="task",
            )
            db.commit()
        except Exception:
            db.rollback()
        logger.error(f"run_auction_ingestion_task echoue: {exc}")
        raise
    finally:
        db.close()
