"""
document_schema.py - Schemas validation Document

Description:
Schemas Pydantic pour lecture des documents uploades.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import date
from app.models.document import TypeDocument


class DocumentResponse(BaseModel):
    id: int
    sci_id: int
    bien_id: Optional[int] = None
    locataire_id: Optional[int] = None
    type_document: TypeDocument
    s3_url: str
    nom_fichier: str
    date_document: Optional[date] = None
    uploaded_at: date
    metadata_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class LocataireDocumentChecklistItem(BaseModel):
    type_document: TypeDocument
    label: str
    required: bool
    uploaded_count: int
    is_complete: bool


class LocataireDocumentChecklistResponse(BaseModel):
    locataire_id: int
    total_required: int
    complete_required: int
    is_complete: bool
    items: list[LocataireDocumentChecklistItem]
