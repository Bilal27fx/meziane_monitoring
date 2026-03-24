"""
bien_routes.py - Routes API gestion Biens immobiliers

Description:
Endpoints CRUD pour les biens immobiliers.
Filtrage possible par SCI et statut.

Dépendances:
- patrimoine_service.py
- schemas.bien_schema

Utilisé par:
- main.py (inclusion router)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.bien_schema import BienCreate, BienUpdate, BienResponse, BienPaginatedResponse
from app.models.bien import StatutBien
from app.services.patrimoine_service import PatrimoineService
from app.utils.db import get_db
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/biens", tags=["Biens"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=BienPaginatedResponse)
def get_all_biens(
    sci_id: Optional[int] = Query(None, description="Filtrer par SCI"),
    statut: Optional[StatutBien] = Query(None, description="Filtrer par statut"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):  # Récupère tous les biens (paginé, filtrable par SCI et statut)
    service = PatrimoineService(db)
    items, total = service.get_all_biens(sci_id=sci_id, statut=statut, limit=limit, offset=offset)
    page = (offset // limit) + 1
    pages = max(1, (total + limit - 1) // limit)
    return BienPaginatedResponse(items=items, total=total, page=page, per_page=limit, pages=pages)


@router.get("/{bien_id}", response_model=BienResponse)
def get_bien(bien_id: int, db: Session = Depends(get_db)):  # Récupère bien par ID
    service = PatrimoineService(db)
    bien = service.get_bien_by_id(bien_id)
    if not bien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bien avec ID {bien_id} introuvable"
        )
    return bien


@router.post("/", response_model=BienResponse, status_code=status.HTTP_201_CREATED)
def create_bien(bien_data: BienCreate, db: Session = Depends(get_db)):  # Crée nouveau bien immobilier
    service = PatrimoineService(db)
    return service.create_bien(bien_data)


@router.put("/{bien_id}", response_model=BienResponse)
def update_bien(bien_id: int, bien_data: BienUpdate, db: Session = Depends(get_db)):  # Met à jour bien existant
    service = PatrimoineService(db)
    bien = service.update_bien(bien_id, bien_data)
    if not bien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bien avec ID {bien_id} introuvable"
        )
    return bien


@router.delete("/{bien_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bien(bien_id: int, db: Session = Depends(get_db)):  # Supprime bien par ID
    service = PatrimoineService(db)
    success = service.delete_bien(bien_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bien avec ID {bien_id} introuvable"
        )
    return None
