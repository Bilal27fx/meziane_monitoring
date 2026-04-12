"""
opportunite_routes.py - Routes API Opportunités

Description:
Endpoints gestion opportunités immobilières agent prospection.
Liste, filtrage, changement statut, stats, lancement agent.

Dépendances:
- agents.agent_prospection
- schemas.opportunite_schema

Utilisé par:
- main.py (inclusion router)
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.schemas.opportunite_schema import (
    OpportuniteResponse,
    OpportuniteUpdateStatut,
    AgentRunResponse,
    OpportuniteStatsResponse,
    StatutOpportunite
)
from app.models.opportunite import Opportunite
from app.utils.db import get_db
from app.utils.logger import setup_logger
from app.utils.auth import get_current_user

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/opportunites", tags=["Opportunités"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[OpportuniteResponse])
def list_opportunites(
    statut: Optional[StatutOpportunite] = Query(None, description="Filtrer par statut"),
    ville: Optional[str] = Query(None, description="Filtrer par ville"),
    score_min: Optional[int] = Query(None, ge=0, le=100, description="Score minimum"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):  # Liste toutes les opportunités avec filtres
    query = db.query(Opportunite)

    if statut:
        query = query.filter(Opportunite.statut == statut)
    if ville:
        query = query.filter(Opportunite.ville.ilike(f"%{ville}%"))
    if score_min is not None:
        query = query.filter(Opportunite.score_global >= score_min)

    query = query.order_by(Opportunite.score_global.desc(), Opportunite.date_detection.desc())

    return query.limit(limit).offset(offset).all()


@router.get("/meilleures", response_model=List[OpportuniteResponse])
def get_meilleures_opportunites(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):  # Top opportunités par score
    return db.query(Opportunite).filter(
        Opportunite.statut.in_([StatutOpportunite.NOUVEAU, StatutOpportunite.VU])
    ).order_by(
        Opportunite.score_global.desc()
    ).limit(limit).all()


@router.get("/stats")
def get_stats_opportunites(db: Session = Depends(get_db)):  # Statistiques opportunités
    total = db.query(func.count(Opportunite.id)).scalar()

    # Par statut
    par_statut = {}
    for statut in StatutOpportunite:
        count = db.query(func.count(Opportunite.id)).filter(
            Opportunite.statut == statut
        ).scalar()
        par_statut[statut.value] = count

    # Par ville (top 10)
    par_ville_raw = db.query(
        Opportunite.ville,
        func.count(Opportunite.id).label('count')
    ).group_by(Opportunite.ville).order_by(func.count(Opportunite.id).desc()).limit(10).all()

    par_ville = {ville: count for ville, count in par_ville_raw}

    # Score moyen
    score_moyen = db.query(func.avg(Opportunite.score_global)).filter(
        Opportunite.score_global.isnot(None)
    ).scalar() or 0

    # Meilleures opportunités
    meilleures = db.query(Opportunite).filter(
        Opportunite.statut.in_([StatutOpportunite.NOUVEAU, StatutOpportunite.VU])
    ).order_by(Opportunite.score_global.desc()).limit(5).all()

    return {
        "total": total,
        "par_statut": par_statut,
        "par_ville": par_ville,
        "score_moyen": round(score_moyen, 2),
        "meilleures_opportunites": meilleures
    }


@router.get("/{opportunite_id}", response_model=OpportuniteResponse)
def get_opportunite(opportunite_id: int, db: Session = Depends(get_db)):  # Récupère opportunité par ID
    opportunite = db.query(Opportunite).filter(Opportunite.id == opportunite_id).first()

    if not opportunite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunité {opportunite_id} introuvable"
        )

    return opportunite


@router.put("/{opportunite_id}/statut", response_model=OpportuniteResponse)
def update_statut(
    opportunite_id: int,
    update_data: OpportuniteUpdateStatut,
    db: Session = Depends(get_db)
):  # Met à jour statut opportunité
    opportunite = db.query(Opportunite).filter(Opportunite.id == opportunite_id).first()

    if not opportunite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunité {opportunite_id} introuvable"
        )

    opportunite.statut = update_data.statut
    if update_data.notes:
        opportunite.notes = update_data.notes

    db.commit()
    db.refresh(opportunite)

    return opportunite


@router.delete("/{opportunite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunite(opportunite_id: int, db: Session = Depends(get_db)):  # Supprime opportunité
    opportunite = db.query(Opportunite).filter(Opportunite.id == opportunite_id).first()

    if not opportunite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunité {opportunite_id} introuvable"
        )

    db.delete(opportunite)
    db.commit()

    return None


@router.post("/agent/run", response_model=AgentRunResponse)
async def run_agent(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):  # Redirige vers le nouveau pipeline LangGraph (POST /auction/agent/run)
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Agent prospection V1 supprimé. Utiliser POST /auction/agent/run (pipeline LangGraph)."
    )
