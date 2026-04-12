"""
auction_agent_routes.py - Routes pilotage agents LangGraph

Description:
Lancement de runs, consultation des runs et de leurs événements.
Déclenche le graphe LangGraph via Celery.

Dépendances:
- fastapi
- models.agent_run, agent_run_event
- tasks.auction_tasks

Utilisé par:
- main.py
- frontend (AuctionRunsPanel)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.utils.db import get_db
from app.models.agent_run import AgentRun, AgentRunStatus
from app.models.agent_run_event import AgentRunEvent
from app.agents.hermes.fetcher import LICITOR_IDF_URL

router = APIRouter(prefix="/auction/agent", tags=["auction-agent"])


class RunRequest(BaseModel):
    source_code: str = "licitor"
    session_urls: Optional[List[str]] = None  # si vide → URL IDF par défaut


@router.post("/run")
def launch_run(payload: RunRequest, db: Session = Depends(get_db)):
    """Lance un run LangGraph via Celery. Utilise l'URL Licitor IDF si session_urls absent."""
    import uuid
    from app.tasks.auction_tasks import run_licitor_graph_task

    # Fallback sur l'URL canonique Licitor IDF
    session_urls = payload.session_urls or [LICITOR_IDF_URL]

    thread_id = str(uuid.uuid4())
    run = AgentRun(
        source_code=payload.source_code,
        status=AgentRunStatus.PENDING,
        parameter_snapshot={"session_urls": session_urls},
        thread_id=thread_id,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    run_licitor_graph_task.delay(run.id)
    return {"run_id": run.id, "thread_id": thread_id, "status": run.status, "session_urls": session_urls}


@router.get("/runs")
def list_runs(limit: int = 20, db: Session = Depends(get_db)):
    """Liste les runs récents."""
    return (
        db.query(AgentRun)
        .order_by(AgentRun.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    """Retourne un run avec ses événements."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run introuvable")
    events = (
        db.query(AgentRunEvent)
        .filter(AgentRunEvent.run_id == run_id)
        .order_by(AgentRunEvent.created_at)
        .all()
    )
    return {"run": run, "events": events}
