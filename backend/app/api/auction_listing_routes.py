"""
auction_listing_routes.py - Routes lecture listings d'enchères

Description:
Consultation des annonces scorées par ORACLE.
Filtres par décision, ville, score, date d'enchère.

Dépendances:
- fastapi
- models.auction_listing

Utilisé par:
- main.py
- frontend (AuctionRunsPanel, OpportunitesWidget)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.utils.db import get_db
from app.models.auction_listing import AuctionListing, AuctionDecision

router = APIRouter(prefix="/auction/listings", tags=["auction-listings"])


@router.get("/")
def list_listings(
    decision: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """Liste les annonces avec filtres optionnels."""
    q = db.query(AuctionListing)
    if decision:
        q = q.filter(AuctionListing.decision == decision)
    if city:
        q = q.filter(AuctionListing.city.ilike(f"%{city}%"))
    if min_score is not None:
        q = q.filter(AuctionListing.score >= min_score)
    q = q.order_by(AuctionListing.score.desc().nullslast())
    return q.offset(offset).limit(limit).all()


@router.get("/{listing_id}")
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """Retourne le détail d'une annonce."""
    from fastapi import HTTPException
    listing = db.query(AuctionListing).filter(AuctionListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing introuvable")
    return listing
