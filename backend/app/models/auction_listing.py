"""
auction_listing.py - Annonce canonique de vente judiciaire

Description:
Représente une annonce issue d'une source d'encheres avec son statut de pipeline.

Dependances:
- utils.db.Base
- auction_source.py
- auction_session.py

Utilise par:
- api/auction_listing_routes.py
"""

from datetime import datetime
import enum

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.utils.db import Base


class AuctionListingStatus(str, enum.Enum):  # Etat de pipeline d'une annonce
    DISCOVERED = "discovered"
    NORMALIZED = "normalized"
    ENRICHED = "enriched"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"


class AuctionListing(Base):  # Annonce normalisee d'enchere
    __tablename__ = "auction_listings"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("auction_sources.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("auction_sessions.id"), nullable=False, index=True)
    external_id = Column(String(120), nullable=True, index=True)
    source_url = Column(String(500), nullable=False, unique=True)
    reference_annonce = Column(String(120), nullable=True)
    title = Column(String(500), nullable=False)
    listing_type = Column(String(80), nullable=True)
    reserve_price = Column(Float, nullable=True)
    city = Column(String(120), nullable=True, index=True)
    postal_code = Column(String(10), nullable=True)
    address = Column(Text, nullable=True)
    surface_m2 = Column(Float, nullable=True)
    nb_pieces = Column(Integer, nullable=True)
    nb_chambres = Column(Integer, nullable=True)
    etage = Column(Integer, nullable=True)
    type_etage = Column(String(80), nullable=True)
    ascenseur = Column(Boolean, nullable=True)
    balcon = Column(Boolean, nullable=True)
    terrasse = Column(Boolean, nullable=True)
    cave = Column(Boolean, nullable=True)
    parking = Column(Boolean, nullable=True)
    box = Column(Boolean, nullable=True)
    jardin = Column(Boolean, nullable=True)
    property_details = Column(JSON, nullable=True)
    occupancy_status = Column(String(80), nullable=True)
    status = Column(Enum(AuctionListingStatus), nullable=False, default=AuctionListingStatus.DISCOVERED)
    published_at = Column(DateTime, nullable=True)
    last_seen_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Dates
    visit_dates = Column(JSON, nullable=True)

    # Scoring LLM
    score_global = Column(Integer, nullable=True, index=True)
    score_localisation = Column(Integer, nullable=True)
    score_prix = Column(Integer, nullable=True)
    score_potentiel = Column(Integer, nullable=True)
    loyer_estime = Column(Float, nullable=True)
    rentabilite_brute = Column(Float, nullable=True)
    raison_score = Column(Text, nullable=True)
    risques_llm = Column(JSON, nullable=True)
    recommandation = Column(String(30), nullable=True)
    scored_at = Column(DateTime, nullable=True)

    source = relationship("AuctionSource", back_populates="listings")
    session = relationship("AuctionSession", back_populates="listings")

    @property
    def auction_date(self):  # Date d'enchère depuis la session liée
        return self.session.session_datetime if self.session else None

    def __repr__(self):
        return f"<AuctionListing {self.id} {self.title[:40]}>"
