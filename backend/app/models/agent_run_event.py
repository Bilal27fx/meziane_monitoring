"""
agent_run_event.py - Événements d'un run agent

Description:
Log structuré des étapes d'un run LangGraph.
Chaque nœud (HERMES, ARCHIVIO, etc.) écrit ses événements ici.

Dépendances:
- sqlalchemy
- models.agent_run

Utilisé par:
- agents/graph/runner.py
- api/auction_agent_routes.py
"""

import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.utils.db import Base


class EventLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class AgentRunEvent(Base):
    __tablename__ = "agent_run_events"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)
    node = Column(String, nullable=False)           # "hermes" | "archivio" | "oracle" | ...
    event = Column(String, nullable=False)          # "started" | "completed" | "error"
    level = Column(Enum(EventLevel), default=EventLevel.INFO)
    message = Column(String)
    payload = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
