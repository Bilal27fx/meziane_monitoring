"""
cashflow_routes.py - Routes API Cashflow

Description:
Endpoints calculs cashflow par bien, SCI, global.
Analytics revenus/dépenses, rentabilité, dashboard.

Dépendances:
- cashflow_service.py
- schemas.cashflow_schema

Utilisé par:
- main.py (inclusion router)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.cashflow_schema import (
    BienCashflowResponse,
    SCICashflowResponse,
    GlobalCashflowResponse,
    CashflowMensuelResponse,
    DepensesCategorieResponse,
    RentabiliteResponse,
    DashboardSummaryResponse
)
from app.services.cashflow_service import CashflowService
from app.utils.db import get_db
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/cashflow", tags=["Cashflow"], dependencies=[Depends(get_current_user)])


@router.get("/bien/{bien_id}", response_model=BienCashflowResponse)
def get_bien_cashflow(
    bien_id: int,
    annee: Optional[int] = Query(None, description="Année"),
    mois: Optional[int] = Query(None, ge=1, le=12, description="Mois (1-12)"),
    db: Session = Depends(get_db)
):  # Récupère cashflow d'un bien
    service = CashflowService(db)
    result = service.get_bien_cashflow(bien_id, annee, mois)
    return result


@router.get("/bien/{bien_id}/mensuel/{annee}", response_model=CashflowMensuelResponse)
def get_bien_cashflow_mensuel(
    bien_id: int,
    annee: int,
    db: Session = Depends(get_db)
):  # Récupère cashflow mensuel d'un bien
    service = CashflowService(db)
    data = service.get_bien_cashflow_mensuel(bien_id, annee)
    return {"data": data}


@router.get("/sci/{sci_id}", response_model=SCICashflowResponse)
def get_sci_cashflow(
    sci_id: int,
    annee: Optional[int] = Query(None, description="Année"),
    mois: Optional[int] = Query(None, ge=1, le=12, description="Mois (1-12)"),
    db: Session = Depends(get_db)
):  # Récupère cashflow d'une SCI
    service = CashflowService(db)
    result = service.get_sci_cashflow(sci_id, annee, mois)
    return result


@router.get("/sci/{sci_id}/mensuel/{annee}", response_model=CashflowMensuelResponse)
def get_sci_cashflow_mensuel(
    sci_id: int,
    annee: int,
    db: Session = Depends(get_db)
):  # Récupère cashflow mensuel d'une SCI
    service = CashflowService(db)
    data = service.get_sci_cashflow_mensuel(sci_id, annee)
    return {"data": data}


@router.get("/global", response_model=GlobalCashflowResponse)
def get_global_cashflow(
    annee: Optional[int] = Query(None, description="Année"),
    mois: Optional[int] = Query(None, ge=1, le=12, description="Mois (1-12)"),
    db: Session = Depends(get_db)
):  # Récupère cashflow global (toutes SCI)
    service = CashflowService(db)
    result = service.get_global_cashflow(annee, mois)
    return result


@router.get("/global/mensuel/{annee}", response_model=CashflowMensuelResponse)
def get_global_cashflow_mensuel(
    annee: int,
    db: Session = Depends(get_db)
):  # Récupère cashflow mensuel global
    service = CashflowService(db)
    data = service.get_global_cashflow_mensuel(annee)
    return {"data": data}


@router.get("/depenses/categorie")
def get_depenses_by_categorie(
    sci_id: Optional[int] = Query(None, description="Filtrer par SCI"),
    bien_id: Optional[int] = Query(None, description="Filtrer par bien"),
    annee: Optional[int] = Query(None, description="Filtrer par année"),
    db: Session = Depends(get_db)
):  # Ventilation dépenses par catégorie
    service = CashflowService(db)
    categories = service.get_depenses_by_categorie(sci_id, bien_id, annee)
    total = sum(categories.values())
    return {
        "categories": categories,
        "total": total
    }


@router.get("/bien/{bien_id}/rentabilite/{annee}", response_model=RentabiliteResponse)
def get_bien_rentabilite(
    bien_id: int,
    annee: int,
    db: Session = Depends(get_db)
):  # Calcule rentabilité d'un bien
    service = CashflowService(db)
    result = service.get_bien_rentabilite(bien_id, annee)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bien avec ID {bien_id} introuvable"
        )

    return result


@router.get("/dashboard/{annee}")
def get_dashboard_summary(
    annee: int,
    db: Session = Depends(get_db)
):  # Récapitulatif complet pour dashboard
    service = CashflowService(db)
    return service.get_dashboard_summary(annee)
