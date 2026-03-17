"""
bien.py - Modèle Bien immobilier

Description:
Représente un bien immobilier (appartement, studio, local) détenu par une SCI.
Contient caractéristiques physiques, valeur, DPE.

Dépendances:
- sci.py (clé étrangère)
- utils.db.Base

Utilisé par:
- patrimoine_service.py
- location_service.py
- acquisition_service.py
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.utils.db import Base
import enum


class TypeBien(str, enum.Enum):  # Types de biens gérés
    APPARTEMENT = "appartement"
    STUDIO = "studio"
    MAISON = "maison"
    LOCAL_COMMERCIAL = "local_commercial"
    IMMEUBLE = "immeuble"
    PARKING = "parking"
    AUTRE = "autre"


class StatutBien(str, enum.Enum):  # Statut occupation bien
    LOUE = "loue"
    VACANT = "vacant"
    TRAVAUX = "travaux"
    VENTE = "vente"


class ClasseDPE(str, enum.Enum):  # Classe énergétique DPE
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    NON_RENSEIGNE = "non_renseigne"


class Bien(Base):  # Représente bien immobilier détenu par SCI
    __tablename__ = "biens"

    id = Column(Integer, primary_key=True, index=True)
    sci_id = Column(Integer, ForeignKey("sci.id"), nullable=False, index=True)

    # Adresse
    adresse = Column(Text, nullable=False)
    ville = Column(String(100), nullable=False, index=True)
    code_postal = Column(String(5), nullable=False)
    complement_adresse = Column(String(200), nullable=True)

    # Caractéristiques
    type_bien = Column(Enum(TypeBien), nullable=False)
    surface = Column(Float, nullable=True)
    nb_pieces = Column(Integer, nullable=True)
    etage = Column(Integer, nullable=True)

    # Financier
    date_acquisition = Column(Date, nullable=True, index=True)
    prix_acquisition = Column(Float, nullable=True)
    valeur_actuelle = Column(Float, nullable=True)

    # DPE & Statut
    dpe_classe = Column(Enum(ClasseDPE), nullable=True)
    dpe_date_validite = Column(Date, nullable=True)
    statut = Column(Enum(StatutBien), nullable=False, default=StatutBien.VACANT)

    # Relations
    sci = relationship("SCI", back_populates="biens")
    transactions = relationship("Transaction", back_populates="bien")
    baux = relationship("Bail", back_populates="bien", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="bien")

    def __repr__(self):
        return f"<Bien {self.type_bien.value} - {self.ville}>"
