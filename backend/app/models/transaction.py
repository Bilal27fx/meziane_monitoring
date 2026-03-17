"""
transaction.py - Modèle Transaction bancaire

Description:
Représente transaction bancaire d'une SCI (loyer, charge, taxe, etc.).
Catégorisée automatiquement par IA pour comptabilité.

Dépendances:
- sci.py, bien.py, locataire.py (clés étrangères)
- utils.db.Base

Utilisé par:
- comptable_service.py
- cashflow_service.py
- banking_connector.py
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from app.utils.db import Base
from datetime import datetime
import enum


class TransactionCategorie(str, enum.Enum):  # Catégories transactions SCI
    LOYER = "loyer"
    CHARGES_COPRO = "charges_copro"
    TAXE_FONCIERE = "taxe_fonciere"
    TRAVAUX = "travaux"
    REMBOURSEMENT_CREDIT = "remboursement_credit"
    ASSURANCE = "assurance"
    HONORAIRES = "honoraires"
    FRAIS_BANCAIRES = "frais_bancaires"
    AUTRE = "autre"


class StatutValidation(str, enum.Enum):  # Statut validation transaction
    EN_ATTENTE = "en_attente"
    VALIDE = "valide"
    REJETE = "rejete"


class Transaction(Base):  # Représente transaction bancaire SCI
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    sci_id = Column(Integer, ForeignKey("sci.id"), nullable=False, index=True)
    compte_bancaire_id = Column(String(100), nullable=False)

    # Transaction
    date = Column(Date, nullable=False, index=True)
    montant = Column(Float, nullable=False)
    libelle = Column(Text, nullable=False)

    # Catégorisation
    categorie = Column(Enum(TransactionCategorie), nullable=True)
    categorie_confidence = Column(Float, nullable=True)

    # Liens optionnels
    bien_id = Column(Integer, ForeignKey("biens.id"), nullable=True, index=True)
    locataire_id = Column(Integer, ForeignKey("locataires.id"), nullable=True)

    # Validation
    statut_validation = Column(Enum(StatutValidation), nullable=False, default=StatutValidation.EN_ATTENTE)
    valide_par = Column(String(100), nullable=True)
    date_validation = Column(Date, nullable=True)

    # Metadata
    created_at = Column(Date, nullable=False, default=datetime.utcnow)

    # Relations
    sci = relationship("SCI", back_populates="transactions")
    bien = relationship("Bien", back_populates="transactions")
    locataire = relationship("Locataire", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.date} - {self.montant}€ - {self.libelle[:30]}>"
