"""
agent_definition.py - Définition d'un agent

Description:
Décrit un agent disponible dans le système (nom, source, description).

Dépendances:
- sqlalchemy

Utilisé par:
- api/auction_agent_routes.py
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.utils.db import Base


class AgentDefinition(Base):
    __tablename__ = "agent_definitions"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)        # "licitor-langgraph"
    source_code = Column(String, nullable=False)              # "licitor"
    description = Column(String)
    is_active = Column(Boolean, default=True)
    default_parameters = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
