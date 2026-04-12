"""
agent_parameter_set.py - Jeu de paramètres pour un run agent

Description:
Paramètres configurables pour lancer un run (URLs, options, filtres).

Dépendances:
- sqlalchemy
- models.agent_definition

Utilisé par:
- api/auction_agent_routes.py
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.utils.db import Base


class AgentParameterSet(Base):
    __tablename__ = "agent_parameter_sets"

    id = Column(Integer, primary_key=True)
    agent_definition_id = Column(Integer, ForeignKey("agent_definitions.id"), nullable=False)
    name = Column(String, nullable=False)                     # "Paris - audiences hebdo"
    parameters = Column(JSONB, default={})                    # {session_urls: [...]}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
