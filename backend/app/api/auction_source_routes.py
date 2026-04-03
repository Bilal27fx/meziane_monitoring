"""
auction_source_routes.py - Routes API sources auctions

Description:
Endpoints de pilotage des sources de ventes judiciaires.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.auction_source import AuctionSource
from app.schemas.auction_schema import AuctionSourceCreate, AuctionSourceResponse
from app.utils.auth import get_current_user
from app.utils.db import get_db

router = APIRouter(prefix="/api/auction-sources", tags=["Auction Sources"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[AuctionSourceResponse])
def list_auction_sources(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return (
        db.query(AuctionSource)
        .order_by(AuctionSource.id.asc())
        .limit(limit)
        .offset(offset)
        .all()
    )


@router.post("/", response_model=AuctionSourceResponse, status_code=status.HTTP_201_CREATED)
def create_auction_source(body: AuctionSourceCreate, db: Session = Depends(get_db)):
    existing = db.query(AuctionSource).filter(AuctionSource.code == body.code).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Source {body.code} deja existante")

    source = AuctionSource(
        code=body.code,
        name=body.name,
        base_url=body.base_url,
        description=body.description,
        status=body.status.value,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source
