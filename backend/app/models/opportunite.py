"""
opportunite.py - Modèle Opportunité immobilière

Description:
Représente annonce immobilière détectée par agent prospection.
Score automatique, suivi statut (nouveau, vu, contacté, rejeté).

Dépendances:
- utils.db.Base

Utilisé par:
- agent_prospection.py
- acquisition_service.py
"""

from sqlalchemy import Column, Integer, String, Float, Date, Enum, Text, JSON
from app.utils.db import Base
from datetime import datetime
import enum


class SourceAnnonce(str, enum.Enum):  # Source annonce immobilière
    SELOGER = "seloger"
    PAP = "pap"
    LEBONCOIN = "leboncoin"
    BIENICI = "bienici"
    LOGIC_IMMO = "logic_immo"
    AUTRE = "autre"


class StatutOpportunite(str, enum.Enum):  # Statut suivi opportunité
    NOUVEAU = "nouveau"
    VU = "vu"
    CONTACTE = "contacte"
    VISITE_PROGRAMMEE = "visite_programmee"
    OFFRE_FAITE = "offre_faite"
    REJETE = "rejete"
    ACQUIS = "acquis"


class Opportunite(Base):  # Représente opportunité immobilière détectée
    __tablename__ = "opportunites_immobilieres"

    id = Column(Integer, primary_key=True, index=True)

    # Source
    url_annonce = Column(String(500), nullable=False, unique=True)
    source = Column(Enum(SourceAnnonce), nullable=False)
    reference_annonce = Column(String(100), nullable=True)

    # Bien
    titre = Column(String(500), nullable=True)
    prix = Column(Float, nullable=False)
    surface = Column(Float, nullable=True)
    prix_m2 = Column(Float, nullable=True)
    ville = Column(String(100), nullable=False, index=True)
    code_postal = Column(String(5), nullable=True)
    adresse = Column(Text, nullable=True)
    nb_pieces = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    photos = Column(Text, nullable=True)  # JSON array URLs

    # Analyse IA
    loyer_estime = Column(Float, nullable=True)
    travaux_estimes = Column(Float, nullable=True)
    rentabilite_brute = Column(Float, nullable=True)
    rentabilite_nette = Column(Float, nullable=True)
    score_rentabilite = Column(Integer, nullable=True)
    score_emplacement = Column(Integer, nullable=True)
    score_etat = Column(Integer, nullable=True)
    score_global = Column(Integer, nullable=True, index=True)
    raison_score = Column(Text, nullable=True)
    risques = Column(JSON, nullable=True)  # Liste de risques (filtrable/indexable)

    # Suivi
    date_detection = Column(Date, nullable=False, default=datetime.utcnow, index=True)
    statut = Column(Enum(StatutOpportunite), nullable=False, default=StatutOpportunite.NOUVEAU)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Opportunite {self.ville} - {self.prix}€ - Score:{self.score_global}>"
