"""
sci_routes.py - Routes API gestion SCI

Description:
Endpoints CRUD pour les SCI (création, lecture, mise à jour, suppression).
Gestion patrimoine immobilier via SCI.

Dépendances:
- patrimoine_service.py
- schemas.sci_schema

Utilisé par:
- main.py (inclusion router)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schemas.sci_schema import SCICreate, SCIUpdate, SCIResponse, SCIPaginatedResponse
from app.services.patrimoine_service import PatrimoineService
from app.utils.db import get_db
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/sci", tags=["SCI"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=SCIPaginatedResponse)
def get_all_sci(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):  # Récupère toutes les SCI (paginé)
    service = PatrimoineService(db)
    items, total = service.get_all_sci(limit=limit, offset=offset)
    page = (offset // limit) + 1
    pages = max(1, (total + limit - 1) // limit)
    return SCIPaginatedResponse(items=items, total=total, page=page, per_page=limit, pages=pages)


@router.get("/{sci_id}", response_model=SCIResponse)
def get_sci(sci_id: int, db: Session = Depends(get_db)):  # Récupère SCI par ID
    service = PatrimoineService(db)
    sci = service.get_sci_by_id(sci_id)
    if not sci:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SCI avec ID {sci_id} introuvable"
        )
    return sci


@router.post("/", response_model=SCIResponse, status_code=status.HTTP_201_CREATED)
def create_sci(sci_data: SCICreate, db: Session = Depends(get_db)):  # Crée nouvelle SCI
    service = PatrimoineService(db)
    return service.create_sci(sci_data)


@router.put("/{sci_id}", response_model=SCIResponse)
def update_sci(sci_id: int, sci_data: SCIUpdate, db: Session = Depends(get_db)):  # Met à jour SCI existante
    service = PatrimoineService(db)
    sci = service.update_sci(sci_id, sci_data)
    if not sci:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SCI avec ID {sci_id} introuvable"
        )
    return sci


@router.delete("/{sci_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sci(sci_id: int, db: Session = Depends(get_db)):  # Supprime SCI par ID
    service = PatrimoineService(db)
    success = service.delete_sci(sci_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SCI avec ID {sci_id} introuvable"
        )
    return None


@router.get("/stats/patrimoine")
def get_patrimoine_stats(db: Session = Depends(get_db)):  # Récupère statistiques patrimoine global
    service = PatrimoineService(db)
    return service.get_patrimoine_stats()
