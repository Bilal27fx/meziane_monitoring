"""
auction_source.py - Source d'enchères judiciaires

Description:
Représente une plateforme source (ex: Licitor).
Contient l'URL de base et le code source utilisé par HERMES.

Dépendances:
- sqlalchemy

Utilisé par:
- agents/graph/runner.py
- api/auction_source_routes.py
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.utils.db import Base


class AuctionSource(Base):
    __tablename__ = "auction_sources"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)        # "licitor"
    name = Column(String, nullable=False)                     # "Licitor"
    base_url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    config = Column(JSONB, default={})                        # config spécifique source
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
