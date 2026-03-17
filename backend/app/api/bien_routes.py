"""
bien_routes.py - Routes API gestion Biens immobiliers

Description:
Endpoints CRUD pour les biens immobiliers.
Filtrage possible par SCI.

Dépendances:
- patrimoine_service.py
- schemas.bien_schema

Utilisé par:
- main.py (inclusion router)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.bien_schema import BienCreate, BienUpdate, BienResponse
from app.services.patrimoine_service import PatrimoineService
from app.utils.db import get_db

router = APIRouter(prefix="/api/biens", tags=["Biens"])


@router.get("/", response_model=List[BienResponse])
def get_all_biens(sci_id: Optional[int] = Query(None, description="Filtrer par SCI"), db: Session = Depends(get_db)):  # Récupère tous les biens (filtrable par SCI)
    service = PatrimoineService(db)
    return service.get_all_biens(sci_id=sci_id)


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
