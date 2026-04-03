"""
auction_session.py - Audience de ventes judiciaires

Description:
Représente une audience source qui regroupe plusieurs annonces d'encheres.

Dependances:
- utils.db.Base
- auction_source.py

Utilise par:
- auction_listing.py
- api/auction_listing_routes.py
"""

from datetime import datetime
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.utils.db import Base


class AuctionSessionStatus(str, enum.Enum):  # Etat de traitement d'une audience
    DISCOVERED = "discovered"
    FETCHED = "fetched"
    PROCESSED = "processed"


class AuctionSession(Base):  # Audience de ventes detectee
    __tablename__ = "auction_sessions"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("auction_sources.id"), nullable=False, index=True)
    external_id = Column(String(120), nullable=True, index=True)
    tribunal = Column(String(160), nullable=False, index=True)
    city = Column(String(120), nullable=True, index=True)
    source_url = Column(String(500), nullable=False, unique=True)
    session_datetime = Column(DateTime, nullable=False, index=True)
    announced_listing_count = Column(Integer, nullable=True)
    status = Column(Enum(AuctionSessionStatus), nullable=False, default=AuctionSessionStatus.DISCOVERED)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    source = relationship("AuctionSource", back_populates="sessions")
    listings = relationship("AuctionListing", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AuctionSession {self.tribunal} {self.session_datetime}>"
