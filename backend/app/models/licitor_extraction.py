"""
licitor_extraction.py - Journal des extractions LLM d'annonces Licitor

Description:
Stocke le payload brut envoyé au LLM, la réponse brute, et l'extraction structurée
pour chaque annonce traitée. Permet le debug et le rejeu sans re-fetcher les pages.

Dependances:
- auction_listing.py
- utils.db.Base

Utilise par:
- auction_ingestion_service.py
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.utils.db import Base


class LicitorExtraction(Base):  # Extraction LLM d'une annonce Licitor
    __tablename__ = "licitor_extractions"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("auction_listings.id"), nullable=False, index=True, unique=True)
    raw_sections = Column(JSON, nullable=True)        # sections envoyées au LLM
    llm_raw_response = Column(Text, nullable=True)    # réponse brute LLM (debug)
    parsed_extraction = Column(JSON, nullable=True)   # LicitorPageExtraction sérialisé
    extraction_model = Column(String(60), nullable=True)
    extracted_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    listing = relationship("AuctionListing", backref="licitor_extraction")
