"""
document_folder.py - Modèle Dossier documentaire

Description:
Structure légère de dossiers pour organiser les documents librement.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.utils.db import Base


class DocumentFolder(Base):
    __tablename__ = "document_folders"

    id = Column(Integer, primary_key=True, index=True)
    sci_id = Column(Integer, ForeignKey("sci.id"), nullable=False, index=True)
    bien_id = Column(Integer, ForeignKey("biens.id"), nullable=True, index=True)
    locataire_id = Column(Integer, ForeignKey("locataires.id"), nullable=True, index=True)
    parent_id = Column(Integer, ForeignKey("document_folders.id"), nullable=True, index=True)
    nom = Column(String(200), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    sci = relationship("SCI", back_populates="document_folders")
    bien = relationship("Bien", back_populates="document_folders")
    locataire = relationship("Locataire", back_populates="document_folders")
    parent = relationship("DocumentFolder", remote_side=[id], back_populates="children")
    children = relationship("DocumentFolder", back_populates="parent")
    documents = relationship("Document", back_populates="folder")

    def __repr__(self):
        return f"<DocumentFolder {self.nom}>"
