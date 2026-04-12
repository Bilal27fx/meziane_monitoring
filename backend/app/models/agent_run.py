"""
agent_run.py - Run d'agent LangGraph

Description:
Représente une exécution du graphe LangGraph.
Tracke le statut, les paramètres, et les résultats du run.

Dépendances:
- sqlalchemy

Utilisé par:
- agents/graph/runner.py
- api/auction_agent_routes.py
- tasks/auction_tasks.py
"""

import enum
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from datetime import datetime
from app.utils.db import Base

# Valeurs uppercase pour correspondre à l'enum PostgreSQL existant "agentrunstatus"
class AgentRunStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

# Référence l'enum PostgreSQL existant sans le recréer
_agent_run_status_pg = ENUM(
    "PENDING", "RUNNING", "SUCCESS", "FAILED", "CANCELLED",
    name="agentrunstatus",
    create_type=False,
)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True)
    source_code = Column(String(80), nullable=True)           # "licitor"
    status = Column(_agent_run_status_pg, default="PENDING")

    # Paramètres d'entrée
    parameter_snapshot = Column(JSONB, default={})            # {session_urls: [...]}

    # Résultats
    result_summary = Column(JSONB, default={})                # compteurs finaux

    # LangGraph thread_id pour checkpointing
    thread_id = Column(String(255), unique=True)

    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    error = Column(Text)
