"""
document_schema.py - Schemas validation Document

Description:
Schemas Pydantic pour lecture des documents uploades.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, datetime
from app.models.document import TypeDocument


class DocumentResponse(BaseModel):
    id: int
    sci_id: int
    bien_id: Optional[int] = None
    locataire_id: Optional[int] = None
    folder_id: Optional[int] = None
    type_document: TypeDocument
    s3_url: str
    nom_fichier: str
    date_document: Optional[date] = None
    uploaded_at: date
    metadata_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class DocumentFolderCreateRequest(BaseModel):
    sci_id: Optional[int] = Field(None, gt=0)
    bien_id: Optional[int] = Field(None, gt=0)
    locataire_id: Optional[int] = Field(None, gt=0)
    parent_id: Optional[int] = Field(None, gt=0)
    nom: str = Field(..., min_length=1, max_length=200)


class DocumentFolderResponse(BaseModel):
    id: int
    sci_id: int
    bien_id: Optional[int] = None
    locataire_id: Optional[int] = None
    parent_id: Optional[int] = None
    nom: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentLibraryResponse(BaseModel):
    current_folder: Optional[DocumentFolderResponse] = None
    folders: list[DocumentFolderResponse]
    documents: list[DocumentResponse]


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
