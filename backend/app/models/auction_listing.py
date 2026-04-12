"""
auction_listing.py - Annonce d'enchère judiciaire

Description:
Représente une annonce individuelle avec toutes les données collectées
par HERMES, enrichies par ARCHIVIO et MERCATO, scorées par ORACLE.

Dépendances:
- sqlalchemy
- models.auction_session

Utilisé par:
- agents/oracle/agent.py (persist)
- api/auction_listing_routes.py
"""

import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from app.utils.db import Base


class AuctionListingStatus(str, enum.Enum):
    DISCOVERED = "discovered"
    SCORED = "scored"
    NOTIFIED = "notified"
    ARCHIVED = "archived"


class AuctionDecision(str, enum.Enum):
    BUY = "BUY"
    WATCH = "WATCH"
    SKIP = "SKIP"


class AuctionListing(Base):
    __tablename__ = "auction_listings"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("auction_sessions.id"), nullable=False)

    # Identifiants
    external_id = Column(String)
    source_url = Column(String, unique=True, nullable=False)

    # Données brutes HERMES
    title = Column(String)
    reserve_price = Column(Float)
    surface_m2 = Column(Float)
    city = Column(String)
    postal_code = Column(String)
    address = Column(String)
    tribunal = Column(String)
    auction_date = Column(DateTime)
    visit_dates = Column(JSONB, default=[])
    visit_location = Column(String)
    occupancy_status = Column(String)          # "libre" | "occupe"
    nb_pieces = Column(Integer)
    etage = Column(Integer)
    type_bien = Column(String)                 # "APPARTEMENT" | "MAISON" | ...
    lawyer_name = Column(String)
    lawyer_phone = Column(String)
    amenities = Column(JSONB, default={})      # {cave, parking, ascenseur, ...}
    property_details = Column(JSONB, default={})

    # Données ARCHIVIO (PDF)
    pdf_data = Column(JSONB, default={})       # charges, DPE, syndic, etc.

    # Données MERCATO (prix marché)
    prix_m2_marche = Column(Float)
    ratio_prix = Column(Float)                 # reserve_price / (surface * prix_m2_marche)
    market_data = Column(JSONB, default={})

    # ORACLE — score et décision
    score = Column(Integer)
    decision = Column(Enum(AuctionDecision))
    score_breakdown = Column(JSONB, default={})
    justification = Column(String)
    deal_breakers = Column(JSONB, default=[])
    flags = Column(JSONB, default=[])

    # Statut et notifications
    status = Column(Enum(AuctionListingStatus), default=AuctionListingStatus.DISCOVERED)
    telegram_notified = Column(Boolean, default=False)
    telegram_notified_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("AuctionSession", back_populates="listings")
