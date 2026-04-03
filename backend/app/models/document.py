"""
document.py - Modèle Document

Description:
Représente document numérisé (facture, bail, KBIS, etc.).
Stocké S3/MinIO avec métadonnées extraites par OCR.

Dépendances:
- sci.py, bien.py (clés étrangères)
- utils.db.Base

Utilisé par:
- document_service.py
- comptable_service.py
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from app.utils.db import Base
from datetime import datetime
import enum


class TypeDocument(str, enum.Enum):  # Types documents gérés
    # SCI / Bien
    FACTURE = "facture"
    RELEVE_BANCAIRE = "releve_bancaire"
    TAXE_FONCIERE = "taxe_fonciere"
    BAIL = "bail"
    DIAGNOSTIC_DPE = "diagnostic_dpe"
    DIAGNOSTIC_AMIANTE = "diagnostic_amiante"
    STATUTS_SCI = "statuts_sci"
    KBIS = "kbis"

    # Locataire
    PIECE_IDENTITE = "piece_identite"
    JUSTIFICATIF_DOMICILE = "justificatif_domicile"
    CONTRAT_TRAVAIL = "contrat_travail"
    FICHE_PAIE = "fiche_paie"
    AVIS_IMPOSITION = "avis_imposition"
    RIB = "rib"
    ASSURANCE_HABITATION = "assurance_habitation"
    ACTE_CAUTION_SOLIDAIRE = "acte_caution_solidaire"
    QUITTANCE_LOYER_PRECEDENTE = "quittance_loyer_precedente"

    AUTRE = "autre"


class Document(Base):  # Représente document numérisé stocké S3
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    sci_id = Column(Integer, ForeignKey("sci.id"), nullable=False, index=True)
    bien_id = Column(Integer, ForeignKey("biens.id"), nullable=True, index=True)
    locataire_id = Column(Integer, ForeignKey("locataires.id"), nullable=True, index=True)
    folder_id = Column(Integer, ForeignKey("document_folders.id"), nullable=True, index=True)

    # Type & Stockage
    type_document = Column(Enum(TypeDocument), nullable=False)
    s3_url = Column(String(500), nullable=False)
    nom_fichier = Column(String(300), nullable=False)

    # Dates
    date_document = Column(Date, nullable=True)
    uploaded_at = Column(Date, nullable=False, default=datetime.utcnow)

    # Métadonnées extraites (OCR)
    metadata_json = Column(JSON, nullable=True)

    # Relations
    sci = relationship("SCI", back_populates="documents")
    bien = relationship("Bien", back_populates="documents")
    locataire = relationship("Locataire", back_populates="documents")
    folder = relationship("DocumentFolder", back_populates="documents")
    extractions = relationship("DocumentExtraction", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document {self.type_document.value} - {self.nom_fichier}>"
