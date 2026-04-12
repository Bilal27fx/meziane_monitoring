"""
runner.py - Point d'entrée pour invoquer le graphe LangGraph

Description:
Fonction invoke() appelée par la task Celery.
Log les événements de run dans agent_run_events.
Met à jour le statut AgentRun.

Dépendances:
- graph/licitor_graph.py
- models.agent_run, agent_run_event
- utils.db

Utilisé par:
- tasks/auction_tasks.py
"""

import os
from datetime import datetime
from app.utils.db import SessionLocal
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def _setup_langsmith():
    """Active le tracing LangSmith si LANGSMITH_API_KEY est configuré."""
    from app.config import settings
    if settings.LANGSMITH_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = settings.LANGCHAIN_TRACING_V2
        os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        logger.info(f"LangSmith tracing activé — project: {settings.LANGCHAIN_PROJECT}")


def invoke(run_id: int, source_code: str, session_urls: list[str]) -> dict:
    """Lance le graphe LangGraph et retourne le state final."""
    _setup_langsmith()

    from app.agents.graph.licitor_graph import licitor_graph
    from app.models.agent_run import AgentRun, AgentRunStatus
    from app.models.agent_run_event import AgentRunEvent, EventLevel

    db = SessionLocal()
    try:
        run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if not run:
            raise ValueError(f"AgentRun {run_id} introuvable")

        # Marquer le run comme démarré
        run.status = AgentRunStatus.RUNNING
        run.started_at = datetime.utcnow()
        _log_event(db, run_id, "runner", "started",
                   f"Lancement graphe — {len(session_urls)} session(s)")
        db.commit()

        initial_state = {
            "run_id": run_id,
            "source_code": source_code,
            "session_urls": session_urls,
            "raw_pages": [],
            "raw_listings": [],
            "pdf_extractions": {},
            "price_estimates": {},
            "scored_listings": [],
            "errors": [],
            "token_usage": {},
            "durations_ms": {},
        }

        config = {"configurable": {"thread_id": run.thread_id or str(run_id)}}

        try:
            final_state = licitor_graph.invoke(initial_state, config=config)
        except Exception as exc:
            run.status = AgentRunStatus.FAILED
            run.finished_at = datetime.utcnow()
            run.error = str(exc)
            _log_event(db, run_id, "runner", "failed", str(exc), EventLevel.ERROR)
            db.commit()
            raise

        _log_event(db, run_id, "runner", "completed",
                   f"Run terminé — {len(final_state.get('scored_listings', []))} listings scorés")
        db.commit()

        return final_state

    finally:
        db.close()


def _log_event(db, run_id: int, node: str, event: str,
               message: str, level=None):
    from app.models.agent_run_event import AgentRunEvent, EventLevel
    ev = AgentRunEvent(
        run_id=run_id,
        node=node,
        event=event,
        level=level or EventLevel.INFO,
        message=message,
    )
    db.add(ev)
