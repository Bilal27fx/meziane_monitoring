"""
agent_run_event.py - Journal persistant des executions d'agents

Description:
Stocke les evenements techniques et metier d'un run pour pilotage dashboard,
debug et audit de progression.
"""

from datetime import datetime
import enum

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.utils.db import Base


class AgentRunEventLevel(str, enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class AgentRunEvent(Base):
    __tablename__ = "agent_run_events"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False, index=True)
    level = Column(Enum(AgentRunEventLevel), nullable=False, default=AgentRunEventLevel.INFO)
    step = Column(String(80), nullable=True, index=True)
    event_type = Column(String(120), nullable=False, index=True)
    message = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    run = relationship("AgentRun", back_populates="events")

    def __repr__(self):
        return f"<AgentRunEvent run={self.run_id} {self.level.value} {self.event_type}>"
