"""
agent_parameter_set.py - Parameter set versionne

Description:
Stocke une configuration versionnee reutilisable pour un agent auctions.

Dependances:
- utils.db.Base
- agent_definition.py

Utilise par:
- agent_run.py
- api/auction_agent_routes.py
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.utils.db import Base


class AgentParameterSet(Base):  # Ensemble de parametres versionne pour un agent
    __tablename__ = "agent_parameter_sets"

    id = Column(Integer, primary_key=True, index=True)
    agent_definition_id = Column(Integer, ForeignKey("agent_definitions.id"), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    is_default = Column(Boolean, nullable=False, default=False)
    parameters_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    agent_definition = relationship("AgentDefinition", back_populates="parameter_sets")
    runs = relationship("AgentRun", back_populates="parameter_set")

    def __repr__(self):
        return f"<AgentParameterSet {self.name} v{self.version}>"
