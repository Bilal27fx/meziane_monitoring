"""
agent_run.py - Execution d'agent

Description:
Historise une execution d'agent avec snapshot des parametres et statut.

Dependances:
- utils.db.Base
- agent_definition.py
- agent_parameter_set.py

Utilise par:
- api/auction_agent_routes.py
"""

from datetime import datetime
import enum

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.utils.db import Base


class AgentRunStatus(str, enum.Enum):  # Etat d'un run
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentTriggerType(str, enum.Enum):  # Type de declenchement
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    BACKFILL = "backfill"


class AgentRun(Base):  # Execution tracee d'un agent
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    agent_definition_id = Column(Integer, ForeignKey("agent_definitions.id"), nullable=False, index=True)
    parameter_set_id = Column(Integer, ForeignKey("agent_parameter_sets.id"), nullable=True, index=True)
    trigger_type = Column(Enum(AgentTriggerType), nullable=False, default=AgentTriggerType.MANUAL)
    status = Column(Enum(AgentRunStatus), nullable=False, default=AgentRunStatus.PENDING)
    parameter_snapshot = Column(JSON, nullable=False, default=dict)
    prompt_snapshot = Column(JSON, nullable=True)
    code_version = Column(String(120), nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    agent_definition = relationship("AgentDefinition", back_populates="runs")
    parameter_set = relationship("AgentParameterSet", back_populates="runs")
    events = relationship("AgentRunEvent", back_populates="run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AgentRun {self.id} {self.status.value}>"
