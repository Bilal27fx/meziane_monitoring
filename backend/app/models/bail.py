"""
bail.py - Modèle Bail locatif

Description:
Représente contrat de location entre bien et locataire.
Suivi loyer, charges, dates, dépôt de garantie.

Dépendances:
- bien.py, locataire.py (clés étrangères)
- utils.db.Base

Utilisé par:
- location_service.py
- cashflow_service.py
"""

from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.utils.db import Base
import enum


class StatutBail(str, enum.Enum):  # Statut contrat de bail
    ACTIF = "actif"
    TERMINE = "termine"
    RESILIE = "resilie"
    PREAVIS = "preavis"


class Bail(Base):  # Représente contrat de location bien-locataire
    __tablename__ = "baux"

    id = Column(Integer, primary_key=True, index=True)
    bien_id = Column(Integer, ForeignKey("biens.id"), nullable=False, index=True)
    locataire_id = Column(Integer, ForeignKey("locataires.id"), nullable=False, index=True)

    # Dates
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=True)
    date_resiliation = Column(Date, nullable=True)

    # Financier
    loyer_mensuel = Column(Float, nullable=False)
    charges_mensuelles = Column(Float, nullable=False, default=0)
    depot_garantie = Column(Float, nullable=True)

    # Statut
    statut = Column(Enum(StatutBail), nullable=False, default=StatutBail.ACTIF)

    # Relations
    bien = relationship("Bien", back_populates="baux")
    locataire = relationship("Locataire", back_populates="baux")
    quittances = relationship("Quittance", back_populates="bail", cascade="all, delete-orphan")
    paiements = relationship("LocatairePaiement", back_populates="bail", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bail {self.locataire.nom} - {self.bien.ville} - {self.loyer_mensuel}€>"
