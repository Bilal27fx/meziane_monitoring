"""
document_extraction.py - Modèle Extraction données document

Description:
Stocke données extraites d'un document par OCR (montant, date, etc.).
Format clé-valeur flexible avec score de confiance.

Dépendances:
- document.py (clé étrangère)
- utils.db.Base

Utilisé par:
- document_service.py
- comptable_service.py
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.utils.db import Base


class DocumentExtraction(Base):  # Représente donnée extraite d'un document
    __tablename__ = "document_extractions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)

    # Extraction
    field_name = Column(String(100), nullable=False)
    field_value = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)

    # Relations
    document = relationship("Document", back_populates="extractions")

    def __repr__(self):
        return f"<Extraction {self.field_name} = {self.field_value}>"
