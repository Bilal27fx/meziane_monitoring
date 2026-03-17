"""
sci.py - Modèle SCI (Société Civile Immobilière)

Description:
Représente une SCI avec ses informations juridiques et financières.
Entité centrale du système liée à biens, transactions, documents.

Dépendances:
- utils.db.Base

Utilisé par:
- patrimoine_service.py
- Tous les modèles liés (bien, transaction, document)
"""

from sqlalchemy import Column, Integer, String, Date, Float, Text
from sqlalchemy.orm import relationship
from app.utils.db import Base


class SCI(Base):  # Représente une SCI avec infos juridiques et relations
    __tablename__ = "sci"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False, unique=True)
    forme_juridique = Column(String(50), nullable=False, default="SCI")
    siret = Column(String(14), nullable=True, unique=True)
    date_creation = Column(Date, nullable=True)
    capital = Column(Float, nullable=True)
    siege_social = Column(Text, nullable=True)
    gerant_nom = Column(String(200), nullable=True)
    gerant_prenom = Column(String(200), nullable=True)

    # Relations
    biens = relationship("Bien", back_populates="sci", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="sci", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="sci", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SCI {self.nom}>"
