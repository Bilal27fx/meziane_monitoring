"""
auction_run_log_service.py - Journalisation persistante des runs auctions

Description:
Fournit un helper unique pour ecrire des evenements de run dans la base et dans
les logs applicatifs.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.agent_run_event import AgentRunEvent, AgentRunEventLevel
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def log_agent_run_event(
    db: Session,
    run_id: int,
    event_type: str,
    message: str,
    *,
    level: AgentRunEventLevel = AgentRunEventLevel.INFO,
    step: str | None = None,
    payload: dict[str, Any] | None = None,
) -> AgentRunEvent:
    event = AgentRunEvent(
        run_id=run_id,
        level=level,
        step=step,
        event_type=event_type,
        message=message,
        payload=payload,
    )
    db.add(event)
    db.flush()

    log_message = f"[run:{run_id}] [{event_type}] {message}"
    if level == AgentRunEventLevel.ERROR:
        logger.error(log_message)
    elif level == AgentRunEventLevel.WARNING:
        logger.warning(log_message)
    elif level == AgentRunEventLevel.DEBUG:
        logger.debug(log_message)
    else:
        logger.info(log_message)

    return event
