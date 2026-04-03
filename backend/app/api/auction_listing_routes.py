"""
auction_listing_routes.py - Routes API listings auctions

Description:
Endpoints de lecture pour audiences et annonces auctions.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.models.auction_listing import AuctionListing
from app.models.auction_session import AuctionSession
from app.schemas.auction_schema import (
    AuctionListingResponse,
    AuctionListingStatus,
    AuctionSessionResponse,
)
from app.utils.auth import get_current_user
from app.utils.db import get_db

router = APIRouter(prefix="/api/auction-data", tags=["Auction Data"], dependencies=[Depends(get_current_user)])


@router.get("/sessions", response_model=list[AuctionSessionResponse])
def list_auction_sessions(
    source_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(AuctionSession)
    if source_id is not None:
        query = query.filter(AuctionSession.source_id == source_id)
    return query.order_by(AuctionSession.session_datetime.desc()).limit(limit).offset(offset).all()


@router.get("/listings", response_model=list[AuctionListingResponse])
def list_auction_listings(
    source_id: int | None = Query(None),
    session_id: int | None = Query(None),
    status_filter: AuctionListingStatus | None = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(AuctionListing)
    if source_id is not None:
        query = query.filter(AuctionListing.source_id == source_id)
    if session_id is not None:
        query = query.filter(AuctionListing.session_id == session_id)
    if status_filter is not None:
        query = query.filter(AuctionListing.status == status_filter)
    return query.order_by(AuctionListing.last_seen_at.desc(), AuctionListing.id.desc()).limit(limit).offset(offset).all()
