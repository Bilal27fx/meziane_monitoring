"""
document_routes.py - Routes API Documents

Description:
Upload/list/suppression des documents SCI/Biens/Locataires avec stockage MinIO.
"""

import json
import os
import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.models.document import Document, TypeDocument
from app.models.document_folder import DocumentFolder
from app.models.sci import SCI
from app.models.bien import Bien
from app.models.bail import Bail
from app.models.locataire import Locataire
from app.schemas.document_schema import (
    DocumentResponse,
    DocumentFolderCreateRequest,
    DocumentFolderResponse,
    DocumentLibraryResponse,
    LocataireDocumentChecklistItem,
    LocataireDocumentChecklistResponse,
)
from app.utils.db import get_db
from app.utils.storage import upload_bytes, get_minio_client, delete_object_by_url
from app.utils.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/documents", tags=["Documents"], dependencies=[Depends(get_current_user)])

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


def _resolve_sci_for_bien(db: Session, bien_id: int, sci_id: Optional[int]) -> int:
    bien = db.query(Bien).filter(Bien.id == bien_id).first()
    if not bien:
        raise HTTPException(status_code=404, detail=f"Bien {bien_id} introuvable")
    if sci_id is not None and bien.sci_id != sci_id:
        raise HTTPException(status_code=400, detail=f"Bien {bien_id} non lie a la SCI {sci_id}")
    return bien.sci_id


def _apply_document_scope(query, model, sci_id: int, bien_id: Optional[int], locataire_id: Optional[int]):
    query = query.filter(model.sci_id == sci_id)
    query = query.filter(model.bien_id == bien_id) if bien_id is not None else query.filter(model.bien_id.is_(None))
    query = query.filter(model.locataire_id == locataire_id) if locataire_id is not None else query.filter(model.locataire_id.is_(None))
    return query


def _resolve_document_context(
    db: Session,
    *,
    sci_id: Optional[int] = None,
    bien_id: Optional[int] = None,
    locataire_id: Optional[int] = None,
    folder_id: Optional[int] = None,
) -> tuple[int, Optional[int], Optional[int], Optional[DocumentFolder]]:
    if folder_id is not None:
        folder = db.query(DocumentFolder).filter(DocumentFolder.id == folder_id).first()
        if not folder:
            raise HTTPException(status_code=404, detail=f"Dossier {folder_id} introuvable")
        return folder.sci_id, folder.bien_id, folder.locataire_id, folder

    if locataire_id is not None:
        locataire = db.query(Locataire).filter(Locataire.id == locataire_id).first()
        if not locataire:
            raise HTTPException(status_code=404, detail=f"Locataire {locataire_id} introuvable")
        resolved_sci_id = _resolve_sci_for_locataire(db, locataire_id=locataire_id, sci_id=sci_id)
        return resolved_sci_id, None, locataire_id, None

    if bien_id is not None:
        resolved_sci_id = _resolve_sci_for_bien(db, bien_id=bien_id, sci_id=sci_id)
        return resolved_sci_id, bien_id, None, None

    if sci_id is not None:
        sci = db.query(SCI).filter(SCI.id == sci_id).first()
        if not sci:
            raise HTTPException(status_code=404, detail=f"SCI {sci_id} introuvable")
        return sci_id, None, None, None

    raise HTTPException(status_code=400, detail="Contexte documents manquant")


def _ensure_folder_parent_scope(parent: DocumentFolder, sci_id: int, bien_id: Optional[int], locataire_id: Optional[int]) -> None:
    if parent.sci_id != sci_id or parent.bien_id != bien_id or parent.locataire_id != locataire_id:
        raise HTTPException(status_code=400, detail="Le dossier parent n'appartient pas au meme contexte")


def _build_document_display_name(custom_name: Optional[str], original_name: Optional[str]) -> str:
    fallback_name = (original_name or "document").strip() or "document"
    desired_name = (custom_name or fallback_name).strip() or fallback_name
    _, original_ext = os.path.splitext(fallback_name)
    _, custom_ext = os.path.splitext(desired_name)
    if original_ext and not custom_ext:
        return f"{desired_name}{original_ext}"
    return desired_name


def _build_document_object_name(
    *,
    sci_id: int,
    bien_id: Optional[int],
    locataire_id: Optional[int],
    folder_id: Optional[int],
    original_filename: Optional[str],
) -> str:
    safe_name = original_filename or "document"
    if folder_id is not None:
        return f"documents/folders/{folder_id}/{uuid.uuid4()}_{safe_name}"
    if locataire_id is not None:
        return f"documents/locataires/{locataire_id}/{uuid.uuid4()}_{safe_name}"
    if bien_id is not None:
        return f"documents/biens/{bien_id}/{uuid.uuid4()}_{safe_name}"
    return f"documents/sci/{sci_id}/{uuid.uuid4()}_{safe_name}"


async def _create_uploaded_document(
    db: Session,
    *,
    file: UploadFile,
    sci_id: Optional[int],
    bien_id: Optional[int],
    locataire_id: Optional[int],
    folder_id: Optional[int],
    nom_document: Optional[str],
    type_document: TypeDocument,
    date_document: Optional[date],
    metadata_json: Optional[str],
) -> Document:
    resolved_sci_id, resolved_bien_id, resolved_locataire_id, folder = _resolve_document_context(
        db,
        sci_id=sci_id,
        bien_id=bien_id,
        locataire_id=locataire_id,
        folder_id=folder_id,
    )

    file_content = await file.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="Fichier vide")

    object_name = _build_document_object_name(
        sci_id=resolved_sci_id,
        bien_id=resolved_bien_id,
        locataire_id=resolved_locataire_id,
        folder_id=folder.id if folder else None,
        original_filename=file.filename,
    )
    file_url = upload_bytes(
        bucket_name=settings.MINIO_BUCKET_DOCUMENTS,
        object_name=object_name,
        content=file_content,
        content_type=file.content_type or "application/octet-stream",
    )

    parsed_metadata = _parse_metadata_json(metadata_json)
    document = Document(
        sci_id=resolved_sci_id,
        bien_id=resolved_bien_id,
        locataire_id=resolved_locataire_id,
        folder_id=folder.id if folder else None,
        type_document=type_document,
        s3_url=file_url,
        nom_fichier=_build_document_display_name(nom_document, file.filename),
        date_document=date_document,
        metadata_json=parsed_metadata,
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/library", response_model=DocumentLibraryResponse)
def get_document_library(
    sci_id: Optional[int] = Query(None),
    bien_id: Optional[int] = Query(None),
    locataire_id: Optional[int] = Query(None),
    folder_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    resolved_sci_id, resolved_bien_id, resolved_locataire_id, folder = _resolve_document_context(
        db,
        sci_id=sci_id,
        bien_id=bien_id,
        locataire_id=locataire_id,
        folder_id=folder_id,
    )
    parent_id = folder.id if folder else None

    folders = (
        _apply_document_scope(
            db.query(DocumentFolder),
            DocumentFolder,
            resolved_sci_id,
            resolved_bien_id,
            resolved_locataire_id,
        )
        .filter(DocumentFolder.parent_id == parent_id)
        .order_by(DocumentFolder.nom.asc(), DocumentFolder.id.asc())
        .all()
    )
    documents = (
        _apply_document_scope(
            db.query(Document),
            Document,
            resolved_sci_id,
            resolved_bien_id,
            resolved_locataire_id,
        )
        .filter(Document.folder_id == parent_id)
        .order_by(Document.uploaded_at.desc(), Document.id.desc())
        .all()
    )

    return DocumentLibraryResponse(
        current_folder=DocumentFolderResponse.model_validate(folder) if folder else None,
        folders=[DocumentFolderResponse.model_validate(item) for item in folders],
        documents=[DocumentResponse.model_validate(item) for item in documents],
    )


@router.post("/folders", response_model=DocumentFolderResponse, status_code=status.HTTP_201_CREATED)
def create_document_folder(body: DocumentFolderCreateRequest, db: Session = Depends(get_db)):
    resolved_sci_id, resolved_bien_id, resolved_locataire_id, _ = _resolve_document_context(
        db,
        sci_id=body.sci_id,
        bien_id=body.bien_id,
        locataire_id=body.locataire_id,
    )

    parent = None
    if body.parent_id is not None:
        parent = db.query(DocumentFolder).filter(DocumentFolder.id == body.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail=f"Dossier parent {body.parent_id} introuvable")
        _ensure_folder_parent_scope(parent, resolved_sci_id, resolved_bien_id, resolved_locataire_id)

    folder = DocumentFolder(
        sci_id=resolved_sci_id,
        bien_id=resolved_bien_id,
        locataire_id=resolved_locataire_id,
        parent_id=parent.id if parent else None,
        nom=body.nom.strip(),
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


@router.get("/sci/{sci_id}", response_model=List[DocumentResponse])
def get_documents_by_sci(sci_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .filter(Document.sci_id == sci_id)
        .order_by(Document.uploaded_at.desc(), Document.id.desc())
        .all()
    )


@router.get("/bien/{bien_id}", response_model=List[DocumentResponse])
def get_documents_by_bien(bien_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .filter(Document.bien_id == bien_id)
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

    uploaded_counts = (
        db.query(
            Document.type_document,
            func.count(Document.id).label("uploaded_count"),
        )
        .filter(Document.locataire_id == locataire_id)
        .group_by(Document.type_document)
        .all()
    )
    counts_by_type: Dict[TypeDocument, int] = {
        doc_type: int(uploaded_count)
        for doc_type, uploaded_count in uploaded_counts
    }

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
    sci_id: Optional[int] = Form(None),
    type_document: TypeDocument = Form(TypeDocument.AUTRE),
    file: UploadFile = File(...),
    bien_id: Optional[int] = Form(None),
    locataire_id: Optional[int] = Form(None),
    folder_id: Optional[int] = Form(None),
    nom_document: Optional[str] = Form(None),
    date_document: Optional[date] = Form(None),
    metadata_json: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    return await _create_uploaded_document(
        db,
        file=file,
        sci_id=sci_id,
        bien_id=bien_id,
        locataire_id=locataire_id,
        folder_id=folder_id,
        nom_document=nom_document,
        type_document=type_document,
        date_document=date_document,
        metadata_json=metadata_json,
    )


@router.post(
    "/upload-locataire",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_locataire_document(
    locataire_id: int = Form(...),
    type_document: TypeDocument = Form(TypeDocument.AUTRE),
    file: UploadFile = File(...),
    sci_id: Optional[int] = Form(None),
    folder_id: Optional[int] = Form(None),
    nom_document: Optional[str] = Form(None),
    date_document: Optional[date] = Form(None),
    metadata_json: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    return await _create_uploaded_document(
        db,
        file=file,
        sci_id=sci_id,
        bien_id=None,
        locataire_id=locataire_id,
        folder_id=folder_id,
        nom_document=nom_document,
        type_document=type_document,
        date_document=date_document,
        metadata_json=metadata_json,
    )


@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    """Stream le fichier depuis MinIO — pour téléchargement (attachment)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} introuvable")

    # Extraire bucket et object_name depuis l'URL stockée
    # URL format: http://minio:9000/{bucket}/{object_name}
    try:
        parts = document.s3_url.split("/", 4)
        bucket_name = parts[3]
        object_name = parts[4]
    except (IndexError, AttributeError):
        raise HTTPException(status_code=500, detail="URL document invalide")

    client = get_minio_client()
    try:
        response = client.get_object(bucket_name, object_name)
    except Exception:
        raise HTTPException(status_code=404, detail="Fichier introuvable dans le stockage")

    ext = (document.nom_fichier or "").lower()
    if ext.endswith(".pdf"):
        media_type = "application/pdf"
    elif ext.endswith((".jpg", ".jpeg")):
        media_type = "image/jpeg"
    elif ext.endswith(".png"):
        media_type = "image/png"
    else:
        media_type = "application/octet-stream"

    return StreamingResponse(
        response,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{document.nom_fichier}"'},
    )


@router.get("/{document_id}/preview")
def preview_document(document_id: int, db: Session = Depends(get_db)):
    """Stream le fichier depuis MinIO — pour prévisualisation inline"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} introuvable")

    try:
        parts = document.s3_url.split("/", 4)
        bucket_name = parts[3]
        object_name = parts[4]
    except (IndexError, AttributeError):
        raise HTTPException(status_code=500, detail="URL document invalide")

    client = get_minio_client()
    try:
        response = client.get_object(bucket_name, object_name)
    except Exception:
        raise HTTPException(status_code=404, detail="Fichier introuvable dans le stockage")

    ext = (document.nom_fichier or "").lower()
    if ext.endswith(".pdf"):
        media_type = "application/pdf"
    elif ext.endswith((".jpg", ".jpeg")):
        media_type = "image/jpeg"
    elif ext.endswith(".png"):
        media_type = "image/png"
    else:
        media_type = "application/octet-stream"

    return StreamingResponse(
        response,
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{document.nom_fichier}"'},
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document {document_id} introuvable")

    try:
        delete_object_by_url(document.s3_url)
    except ValueError:
        raise HTTPException(status_code=500, detail="URL document invalide")
    except Exception:
        raise HTTPException(status_code=502, detail="Suppression stockage impossible")

    db.delete(document)
    db.commit()
    return None


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_folder(folder_id: int, db: Session = Depends(get_db)):
    folder = db.query(DocumentFolder).filter(DocumentFolder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail=f"Dossier {folder_id} introuvable")

    has_children = db.query(DocumentFolder.id).filter(DocumentFolder.parent_id == folder_id).first()
    has_documents = db.query(Document.id).filter(Document.folder_id == folder_id).first()
    if has_children or has_documents:
        raise HTTPException(status_code=409, detail="Le dossier doit etre vide avant suppression")

    db.delete(folder)
    db.commit()
    return None
