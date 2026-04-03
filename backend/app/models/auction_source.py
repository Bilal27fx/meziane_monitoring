"""
auction_source.py - Source de collecte auctions

Description:
Décrit une source externe de ventes judiciaires et son état d'activation.

Dependances:
- utils.db.Base

Utilise par:
- auction_session.py
- api/auction_source_routes.py
"""

from datetime import datetime
import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import relationship

from app.utils.db import Base


class AuctionSourceStatus(str, enum.Enum):  # Etat d'une source de collecte
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class AuctionSource(Base):  # Source externe de ventes aux encheres
    __tablename__ = "auction_sources"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(120), nullable=False)
    base_url = Column(String(500), nullable=False)
    status = Column(Enum(AuctionSourceStatus), nullable=False, default=AuctionSourceStatus.ACTIVE)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions = relationship("AuctionSession", back_populates="source", cascade="all, delete-orphan")
    listings = relationship("AuctionListing", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AuctionSource {self.code} ({self.status.value})>"
