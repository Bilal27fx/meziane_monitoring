"""
locataire.py - Modèle Locataire

Description:
Représente un locataire avec informations personnelles et professionnelles.
Lié aux baux locatifs et transactions de loyers.

Dépendances:
- utils.db.Base

Utilisé par:
- location_service.py
- bail.py
- transaction.py
"""

from sqlalchemy import Column, Integer, String, Date, Float, Text
from sqlalchemy.orm import relationship
from app.utils.db import Base


class Locataire(Base):  # Représente locataire avec infos personnelles
    __tablename__ = "locataires"

    id = Column(Integer, primary_key=True, index=True)

    # Identité
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(200), nullable=True, unique=True)
    telephone = Column(String(20), nullable=True)
    date_naissance = Column(Date, nullable=True)

    # Professionnel
    profession = Column(String(200), nullable=True)
    revenus_annuels = Column(Float, nullable=True)

    # Relations
    baux = relationship("Bail", back_populates="locataire", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="locataire")
    documents = relationship("Document", back_populates="locataire")

    def __repr__(self):
        return f"<Locataire {self.prenom} {self.nom}>"
