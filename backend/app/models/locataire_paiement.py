"""
locataire_paiement.py - Modèle Paiement locataire

Description:
Trace les règlements réellement encaissés pour un locataire, avec rattachement
au bail actif et éventuellement à une quittance précise.
"""

from datetime import datetime
import enum

from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, Enum, String
from sqlalchemy.orm import relationship

from app.utils.db import Base


class ModePaiement(str, enum.Enum):
    VIREMENT = "virement"
    PRELEVEMENT = "prelevement"
    CARTE = "carte"
    CHEQUE = "cheque"
    ESPECES = "especes"
    AUTRE = "autre"


class LocatairePaiement(Base):
    __tablename__ = "locataire_paiements"

    id = Column(Integer, primary_key=True, index=True)
    locataire_id = Column(Integer, ForeignKey("locataires.id"), nullable=False, index=True)
    bail_id = Column(Integer, ForeignKey("baux.id"), nullable=False, index=True)
    quittance_id = Column(Integer, ForeignKey("quittances.id"), nullable=True, index=True)

    date_paiement = Column(Date, nullable=False, index=True)
    montant = Column(Float, nullable=False)
    mode_paiement = Column(Enum(ModePaiement), nullable=False, default=ModePaiement.VIREMENT)
    reference = Column(String(120), nullable=True)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    locataire = relationship("Locataire", back_populates="paiements")
    bail = relationship("Bail", back_populates="paiements")
    quittance = relationship("Quittance", back_populates="paiements")

    def __repr__(self):
        return f"<LocatairePaiement locataire={self.locataire_id} montant={self.montant} date={self.date_paiement}>"
