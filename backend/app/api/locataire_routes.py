"""
locataire_routes.py - Routes API gestion Locataires

Description:
Endpoints CRUD pour les locataires.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schemas.locataire_schema import LocataireCreate, LocataireUpdate, LocataireResponse, LocatairePaginatedResponse
from app.services.patrimoine_service import PatrimoineService
from app.utils.db import get_db
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/locataires", tags=["Locataires"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=LocatairePaginatedResponse)
def get_all_locataires(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):  # Paginé
    service = PatrimoineService(db)
    items, total = service.get_all_locataires(limit=limit, offset=offset)
    page = (offset // limit) + 1
    pages = max(1, (total + limit - 1) // limit)
    return LocatairePaginatedResponse(items=items, total=total, page=page, per_page=limit, pages=pages)


@router.get("/{locataire_id}", response_model=LocataireResponse)
def get_locataire(locataire_id: int, db: Session = Depends(get_db)):
    service = PatrimoineService(db)
    locataire = service.get_locataire_by_id(locataire_id)
    if not locataire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Locataire avec ID {locataire_id} introuvable"
        )
    return locataire


@router.post("/", response_model=LocataireResponse, status_code=status.HTTP_201_CREATED)
def create_locataire(locataire_data: LocataireCreate, db: Session = Depends(get_db)):
    service = PatrimoineService(db)
    return service.create_locataire(locataire_data)


@router.put("/{locataire_id}", response_model=LocataireResponse)
def update_locataire(locataire_id: int, locataire_data: LocataireUpdate, db: Session = Depends(get_db)):
    service = PatrimoineService(db)
    locataire = service.update_locataire(locataire_id, locataire_data)
    if not locataire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Locataire avec ID {locataire_id} introuvable"
        )
    return locataire


@router.delete("/{locataire_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_locataire(locataire_id: int, db: Session = Depends(get_db)):
    service = PatrimoineService(db)
    success = service.delete_locataire(locataire_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Locataire avec ID {locataire_id} introuvable"
        )
    return None
