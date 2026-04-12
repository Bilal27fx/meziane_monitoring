"""
auction_source_routes.py - Routes CRUD sources d'enchères

Description:
Gestion des sources (Licitor, etc.) : liste, création, activation.

Dépendances:
- fastapi
- models.auction_source

Utilisé par:
- main.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.auction_source import AuctionSource

router = APIRouter(prefix="/auction/sources", tags=["auction-sources"])


@router.get("/")
def list_sources(db: Session = Depends(get_db)):
    """Liste toutes les sources d'enchères."""
    return db.query(AuctionSource).all()


@router.get("/{source_id}")
def get_source(source_id: int, db: Session = Depends(get_db)):
    """Retourne une source par ID."""
    source = db.query(AuctionSource).filter(AuctionSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source introuvable")
    return source


@router.post("/")
def create_source(payload: dict, db: Session = Depends(get_db)):
    """Crée une nouvelle source."""
    source = AuctionSource(**payload)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source
