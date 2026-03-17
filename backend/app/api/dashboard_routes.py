"""
dashboard_routes.py - Routes API Dashboard

Description:
Endpoints pour dashboard Bloomberg-style avec KPI, graphiques, analytics.
Agrégation données patrimoine, cashflow, transactions, locataires, opportunités.

Dépendances:
- dashboard_service.py
- schemas.dashboard_schema

Utilisé par:
- main.py (inclusion router)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas.dashboard_schema import (
    KPIResponse,
    Cashflow30DaysResponse,
    Patrimoine12MonthsResponse,
    RecentTransactionsResponse,
    TopBiensResponse,
    SCIOverviewResponse,
    LocatairesOverviewResponse,
    OpportunitesOverviewResponse,
    FullDashboardResponse
)
from app.services.dashboard_service import DashboardService
from app.utils.db import get_db
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/kpi", response_model=KPIResponse)
def get_dashboard_kpi(db: Session = Depends(get_db)):
    """
    Récupère tous les KPI principaux du dashboard

    Returns:
        - patrimoine_net: Valeur totale du patrimoine
        - cashflow_today: Cashflow cumulé du mois en cours
        - nb_alertes: Nombre d'alertes actives (impayés + opportunités)
        - performance_ytd: Performance année en cours (%)
        - taux_occupation: Taux d'occupation des biens (%)
        - nb_locataires_actifs: Nombre de locataires actifs
    """
    try:
        service = DashboardService(db)
        return service.get_kpi()
    except Exception as e:
        logger.error(f"Erreur récupération KPI: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du calcul des KPI: {str(e)}"
        )


@router.get("/cashflow", response_model=Cashflow30DaysResponse)
def get_dashboard_cashflow(db: Session = Depends(get_db)):
    """
    Récupère données cashflow pour les 30 derniers jours

    Returns:
        Liste de points de données avec date, revenus, dépenses, net
        pour chaque jour des 30 derniers jours
    """
    try:
        service = DashboardService(db)
        data = service.get_cashflow_30days()
        return {"data": data}
    except Exception as e:
        logger.error(f"Erreur récupération cashflow 30j: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du calcul du cashflow: {str(e)}"
        )


@router.get("/patrimoine", response_model=Patrimoine12MonthsResponse)
def get_dashboard_patrimoine(db: Session = Depends(get_db)):
    """
    Récupère évolution patrimoine sur 12 derniers mois

    Returns:
        Liste de points avec mois et valeur du patrimoine
    """
    try:
        service = DashboardService(db)
        data = service.get_patrimoine_12months()
        return {"data": data}
    except Exception as e:
        logger.error(f"Erreur récupération patrimoine 12m: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du calcul du patrimoine: {str(e)}"
        )


@router.get("/transactions", response_model=RecentTransactionsResponse)
def get_dashboard_transactions(
    limit: int = Query(10, ge=1, le=50, description="Nombre de transactions à retourner"),
    db: Session = Depends(get_db)
):
    """
    Récupère les dernières transactions

    Args:
        limit: Nombre maximum de transactions (1-50, défaut: 10)

    Returns:
        Liste des dernières transactions avec détails
    """
    try:
        service = DashboardService(db)
        data = service.get_recent_transactions(limit)
        return {"data": data}
    except Exception as e:
        logger.error(f"Erreur récupération transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des transactions: {str(e)}"
        )


@router.get("/biens/top5", response_model=TopBiensResponse)
def get_dashboard_top_biens(
    limit: int = Query(5, ge=1, le=20, description="Nombre de biens à retourner"),
    db: Session = Depends(get_db)
):
    """
    Récupère top biens par rentabilité

    Args:
        limit: Nombre maximum de biens (1-20, défaut: 5)

    Returns:
        Liste des meilleurs biens triés par rentabilité nette décroissante
    """
    try:
        service = DashboardService(db)
        data = service.get_top_biens_by_rentabilite(limit)
        return {"data": data}
    except Exception as e:
        logger.error(f"Erreur récupération top biens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du calcul des top biens: {str(e)}"
        )


@router.get("/sci/overview", response_model=SCIOverviewResponse)
def get_dashboard_sci_overview(db: Session = Depends(get_db)):
    """
    Récupère vue d'ensemble de toutes les SCI

    Returns:
        Liste des SCI avec KPI (nb biens, valeur, cashflow, revenus, dépenses)
    """
    try:
        service = DashboardService(db)
        data = service.get_sci_overview()
        return {"data": data}
    except Exception as e:
        logger.error(f"Erreur récupération SCI overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des SCI: {str(e)}"
        )


@router.get("/locataires", response_model=LocatairesOverviewResponse)
def get_dashboard_locataires(db: Session = Depends(get_db)):
    """
    Récupère liste des locataires avec statut paiement

    Returns:
        Liste des locataires actifs avec infos bail et statut paiement
    """
    try:
        service = DashboardService(db)
        data = service.get_locataires_overview()
        return {"data": data}
    except Exception as e:
        logger.error(f"Erreur récupération locataires: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des locataires: {str(e)}"
        )


@router.get("/opportunites", response_model=OpportunitesOverviewResponse)
def get_dashboard_opportunites(
    limit: int = Query(10, ge=1, le=50, description="Nombre d'opportunités à retourner"),
    db: Session = Depends(get_db)
):
    """
    Récupère top opportunités détectées par agent IA

    Args:
        limit: Nombre maximum d'opportunités (1-50, défaut: 10)

    Returns:
        Liste des meilleures opportunités triées par score décroissant
    """
    try:
        service = DashboardService(db)
        data = service.get_opportunites_overview(limit)
        return {"data": data}
    except Exception as e:
        logger.error(f"Erreur récupération opportunités: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des opportunités: {str(e)}"
        )


@router.get("/full", response_model=FullDashboardResponse)
def get_full_dashboard(db: Session = Depends(get_db)):
    """
    Récupère TOUTES les données du dashboard en une seule requête

    Returns:
        Objet complet avec:
        - KPI
        - Cashflow 30 jours
        - Patrimoine 12 mois
        - Dernières transactions
        - Top biens
        - Vue SCI
        - Locataires
        - Opportunités

    Note: Endpoint optimisé pour charger le dashboard en une seule requête HTTP
    """
    try:
        service = DashboardService(db)
        return service.get_full_dashboard()
    except Exception as e:
        logger.error(f"Erreur récupération dashboard complet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du dashboard: {str(e)}"
        )
