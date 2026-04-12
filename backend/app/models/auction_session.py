"""
auction_session.py - Session d'enchères judiciaires

Description:
Représente une audience (tribunal + date).
Une session contient plusieurs listings.

Dépendances:
- sqlalchemy
- models.auction_source

Utilisé par:
- agents/oracle/agent.py (persist)
- api/auction_listing_routes.py
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.utils.db import Base


class AuctionSession(Base):
    __tablename__ = "auction_sessions"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("auction_sources.id"), nullable=False)
    external_id = Column(String, nullable=False)
    tribunal = Column(String)
    city = Column(String)
    session_datetime = Column(DateTime)
    source_url = Column(String, nullable=False)
    announced_listing_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listings = relationship("AuctionListing", back_populates="session")
