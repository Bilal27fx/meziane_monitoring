"""
agent_definition.py - Definition d'agent pilotable

Description:
Décrit un agent logique de la plateforme auctions avec son role et son activation.

Dependances:
- utils.db.Base

Utilise par:
- agent_parameter_set.py
- agent_run.py
- api/auction_agent_routes.py
"""

from datetime import datetime
import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import relationship

from app.utils.db import Base


class AgentType(str, enum.Enum):  # Type fonctionnel d'agent
    INGESTION = "ingestion"
    ENRICHMENT = "enrichment"
    ANALYSIS = "analysis"
    RANKING = "ranking"
    ORCHESTRATION = "orchestration"


class AgentStatus(str, enum.Enum):  # Etat d'activation d'un agent
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class AgentDefinition(Base):  # Definition fonctionnelle d'un agent
    __tablename__ = "agent_definitions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(80), nullable=False, unique=True, index=True)
    name = Column(String(160), nullable=False)
    agent_type = Column(Enum(AgentType), nullable=False)
    status = Column(Enum(AgentStatus), nullable=False, default=AgentStatus.ACTIVE)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    parameter_sets = relationship("AgentParameterSet", back_populates="agent_definition", cascade="all, delete-orphan")
    runs = relationship("AgentRun", back_populates="agent_definition", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AgentDefinition {self.code} ({self.agent_type.value})>"
