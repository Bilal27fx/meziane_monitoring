"""
document_routes.py - Routes API Documents

Description:
Upload/list/suppression des documents SCI/Biens/Locataires avec stockage MinIO.
"""

import json
import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.models.document import Document, TypeDocument
from app.models.sci import SCI
from app.models.bien import Bien
from app.models.bail import Bail
from app.models.locataire import Locataire
from app.schemas.document_schema import (
    DocumentResponse,
    LocataireDocumentChecklistItem,
    LocataireDocumentChecklistResponse,
)
from app.utils.db import get_db
from app.utils.storage import upload_bytes
from app.config import settings

router = APIRouter(prefix="/api/documents", tags=["Documents"])

LOCATAIRE_REQUIRED_DOCUMENTS: List[TypeDocument] = [
    TypeDocument.PIECE_IDENTITE,
    TypeDocument.JUSTIFICATIF_DOMICILE,
    TypeDocument.CONTRAT_TRAVAIL,
    TypeDocument.FICHE_PAIE,
    TypeDocument.AVIS_IMPOSITION,
    TypeDocument.RIB,
    TypeDocument.ASSURANCE_HABITATION,
]

LOCATAIRE_OPTIONAL_DOCUMENTS: List[TypeDocument] = [
    TypeDocument.ACTE_CAUTION_SOLIDAIRE,
    TypeDocument.QUITTANCE_LOYER_PRECEDENTE,
    TypeDocument.BAIL,
    TypeDocument.AUTRE,
]

LOCATAIRE_ALLOWED_DOCUMENTS = set(LOCATAIRE_REQUIRED_DOCUMENTS + LOCATAIRE_OPTIONAL_DOCUMENTS)

LOCATAIRE_DOCUMENT_LABELS: Dict[TypeDocument, str] = {
    TypeDocument.PIECE_IDENTITE: "Piece d'identite",
    TypeDocument.JUSTIFICATIF_DOMICILE: "Justificatif de domicile",
    TypeDocument.CONTRAT_TRAVAIL: "Contrat de travail",
    TypeDocument.FICHE_PAIE: "Fiches de paie",
    TypeDocument.AVIS_IMPOSITION: "Avis d'imposition",
    TypeDocument.RIB: "RIB",
    TypeDocument.ASSURANCE_HABITATION: "Assurance habitation",
    TypeDocument.ACTE_CAUTION_SOLIDAIRE: "Acte de caution solidaire",
    TypeDocument.QUITTANCE_LOYER_PRECEDENTE: "Quittance de loyer precedente",
    TypeDocument.BAIL: "Bail",
    TypeDocument.AUTRE: "Autre document",
}


def _parse_metadata_json(metadata_json: Optional[str]) -> Optional[dict]:
    if not metadata_json:
        return None
    try:
        return json.loads(metadata_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="metadata_json invalide")


def _resolve_sci_for_locataire(db: Session, locataire_id: int, sci_id: Optional[int]) -> int:
    if sci_id is not None:
        sci = db.query(SCI).filter(SCI.id == sci_id).first()
        if not sci:
            raise HTTPException(status_code=404, detail=f"SCI {sci_id} introuvable")
        return sci_id

    sci_ids = (
        db.query(Bien.sci_id)
        .join(Bail, Bail.bien_id == Bien.id)
        .filter(Bail.locataire_id == locataire_id)
        .distinct()
        .all()
    )
    unique_sci_ids = [row[0] for row in sci_ids if row[0] is not None]

    if len(unique_sci_ids) == 1:
        return unique_sci_ids[0]
    if len(unique_sci_ids) == 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Aucune SCI deduite pour ce locataire. "
                "Renseigne sci_id ou cree un bail lie a un bien."
            ),
        )
    raise HTTPException(
        status_code=400,
        detail="Plusieurs SCI liees a ce locataire. Precise sci_id.",
    )


@router.get("/sci/{sci_id}", response_model=List[DocumentResponse])
def get_documents_by_sci(sci_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .filter(Document.sci_id == sci_id)
        .order_by(Document.uploaded_at.desc(), Document.id.desc())
        .all()
    )


@router.get("/locataire/{locataire_id}", response_model=List[DocumentResponse])
def get_documents_by_locataire(locataire_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .filter(Document.locataire_id == locataire_id)
        .order_by(Document.uploaded_at.desc(), Document.id.desc())
        .all()
    )


@router.get(
    "/locataire/{locataire_id}/checklist",
    response_model=LocataireDocumentChecklistResponse,
)
def get_locataire_documents_checklist(locataire_id: int, db: Session = Depends(get_db)):
    locataire = db.query(Locataire).filter(Locataire.id == locataire_id).first()
    if not locataire:
        raise HTTPException(status_code=404, detail=f"Locataire {locataire_id} introuvable")

    uploaded_docs = (
        db.query(Document)
        .filter(Document.locataire_id == locataire_id)
        .all()
    )
    counts_by_type: Dict[TypeDocument, int] = {}
    for doc in uploaded_docs:
        counts_by_type[doc.type_document] = counts_by_type.get(doc.type_document, 0) + 1

    all_types = LOCATAIRE_REQUIRED_DOCUMENTS + LOCATAIRE_OPTIONAL_DOCUMENTS
    items: List[LocataireDocumentChecklistItem] = []
    for doc_type in all_types:
        uploaded_count = counts_by_type.get(doc_type, 0)
        is_required = doc_type in LOCATAIRE_REQUIRED_DOCUMENTS
        items.append(
            LocataireDocumentChecklistItem(
                type_document=doc_type,
                label=LOCATAIRE_DOCUMENT_LABELS.get(doc_type, doc_type.value),
                required=is_required,
                uploaded_count=uploaded_count,
                is_complete=(uploaded_count > 0) if is_required else True,
            )
        )

    total_required = len(LOCATAIRE_REQUIRED_DOCUMENTS)
    complete_required = sum(1 for item in items if item.required and item.is_complete)

    return LocataireDocumentChecklistResponse(
        locataire_id=locataire_id,
        total_required=total_required,
        complete_required=complete_required,
        is_complete=(complete_required == total_required),
        items=items,
    )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    sci_id: int = Form(...),
    type_document: TypeDocument = Form(...),
    file: UploadFile = File(...),
    bien_id: Optional[int] = Form(None),
    date_document: Optional[date] = Form(None),
    metadata_json: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    sci = db.query(SCI).filter(SCI.id == sci_id).first()
    if not sci:
        raise HTTPException(status_code=404, detail=f"SCI {sci_id} introuvable")

    if bien_id is not None:
        bien = db.query(Bien).filter(Bien.id == bien_id, Bien.sci_id == sci_id).first()
        if not bien:
            raise HTTPException(
                status_code=400,
                detail=f"Bien {bien_id} non lie a la SCI {sci_id}",
            )

    file_content = await file.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="Fichier vide")

    object_name = f"sci/{sci_id}/{uuid.uuid4()}_{file.filename}"
    file_url = upload_bytes(
        bucket_name=settings.MINIO_BUCKET_DOCUMENTS,
        object_name=object_name,
        content=file_content,
        content_type=file.content_type or "application/octet-stream",
    )

    parsed_metadata = _parse_metadata_json(metadata_json)

    document = Document(
        sci_id=sci_id,
        bien_id=bien_id,
        type_document=type_document,
        s3_url=file_url,
        nom_fichier=file.filename or object_name,
        date_document=date_document,
        metadata_json=parsed_metadata,
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.post(
    "/upload-locataire",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_locataire_document(
    locataire_id: int = Form(...),
    type_document: TypeDocument = Form(...),
    file: UploadFile = File(...),
    sci_id: Optional[int] = Form(None),
    date_document: Optional[date] = Form(None),
    metadata_json: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    locataire = db.query(Locataire).filter(Locataire.id == locataire_id).first()
    if not locataire:
        raise HTTPException(status_code=404, detail=f"Locataire {locataire_id} introuvable")

    if type_document not in LOCATAIRE_ALLOWED_DOCUMENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Type de document non autorise pour un locataire: {type_document.value}",
        )

    resolved_sci_id = _resolve_sci_for_locataire(db, locataire_id=locataire_id, sci_id=sci_id)

    file_content = await file.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="Fichier vide")

    object_name = f"locataires/{locataire_id}/{uuid.uuid4()}_{file.filename}"
    file_url = upload_bytes(
        bucket_name=settings.MINIO_BUCKET_DOCUMENTS,
        object_name=object_name,
        content=file_content,
        content_type=file.content_type or "application/octet-stream",
    )

    parsed_metadata = _parse_metadata_json(metadata_json)

    document = Document(
        sci_id=resolved_sci_id,
        locataire_id=locataire_id,
        type_document=type_document,
        s3_url=file_url,
        nom_fichier=file.filename or object_name,
        date_document=date_document,
        metadata_json=parsed_metadata,
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} introuvable")

    db.delete(document)
    db.commit()
    return None
