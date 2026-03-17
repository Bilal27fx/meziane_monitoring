"""
quittance.py - Modèle Quittance de loyer

Description:
Représente paiement mensuel de loyer par locataire.
Suivi statut paiement (payé, impayé, partiel).

Dépendances:
- bail.py (clé étrangère)
- utils.db.Base

Utilisé par:
- location_service.py
- cashflow_service.py
"""

from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Enum, String
from sqlalchemy.orm import relationship
from app.utils.db import Base
import enum


class StatutQuittance(str, enum.Enum):  # Statut paiement loyer
    EN_ATTENTE = "en_attente"
    PAYE = "paye"
    IMPAYE = "impaye"
    PARTIEL = "partiel"


class Quittance(Base):  # Représente quittance loyer mensuelle
    __tablename__ = "quittances"

    id = Column(Integer, primary_key=True, index=True)
    bail_id = Column(Integer, ForeignKey("baux.id"), nullable=False, index=True)

    # Période
    mois = Column(Integer, nullable=False)
    annee = Column(Integer, nullable=False)

    # Montants
    montant_loyer = Column(Float, nullable=False)
    montant_charges = Column(Float, nullable=False, default=0)
    montant_total = Column(Float, nullable=False)

    # Paiement
    date_paiement = Column(Date, nullable=True)
    montant_paye = Column(Float, nullable=True)
    statut = Column(Enum(StatutQuittance), nullable=False, default=StatutQuittance.EN_ATTENTE)

    # Metadata
    fichier_url = Column(String(500), nullable=True)

    # Relations
    bail = relationship("Bail", back_populates="quittances")

    def __repr__(self):
        return f"<Quittance {self.annee}-{self.mois:02d} - {self.montant_total}€ - {self.statut.value}>"
