"""
auction_tasks.py - Tasks Celery pipeline LangGraph enchères

Description:
Task asynchrone qui déclenche le graphe LangGraph via runner.invoke().
Référencé par api/auction_agent_routes.py.

Dépendances:
- celery_app
- agents/graph/runner.py

Utilisé par:
- api/auction_agent_routes.py
- celery beat (futur scheduling)
"""

from app.tasks.celery_app import celery_app
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


@celery_app.task(
    name="app.tasks.auction_tasks.run_licitor_graph_task",
    bind=True,
    max_retries=1,
    soft_time_limit=600,  # 10 minutes max
)
def run_licitor_graph_task(self, run_id: int):
    """Lance le pipeline LangGraph pour un run d'enchères Licitor."""
    from app.utils.db import SessionLocal
    from app.models.agent_run import AgentRun

    logger.info(f"[auction_task] Démarrage run_id={run_id}")

    db = SessionLocal()
    try:
        run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if not run:
            raise ValueError(f"AgentRun {run_id} introuvable")

        source_code = run.source_code
        session_urls = run.parameter_snapshot.get("session_urls", [])
    finally:
        db.close()

    try:
        from app.agents.graph.runner import invoke
        result = invoke(
            run_id=run_id,
            source_code=source_code,
            session_urls=session_urls,
        )
        logger.info(f"[auction_task] run_id={run_id} terminé — "
                    f"{len(result.get('scored_listings', []))} listings scorés")
        return {
            "run_id": run_id,
            "scored": len(result.get("scored_listings", [])),
        }
    except Exception as exc:
        logger.error(f"[auction_task] run_id={run_id} échoué: {exc}")
        raise self.retry(exc=exc, countdown=0, max_retries=0)
