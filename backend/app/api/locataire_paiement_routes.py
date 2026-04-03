"""
locataire_paiement_routes.py - Routes API paiements locataire
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.locataire_paiement_schema import (
    LocatairePaiementCreate,
    LocatairePaiementOverviewResponse,
    LocatairePaiementResponse,
)
from app.services.locataire_paiement_service import LocatairePaiementService
from app.utils.auth import get_current_user
from app.utils.db import get_db

router = APIRouter(prefix="/api/locataires", tags=["Paiements locataires"], dependencies=[Depends(get_current_user)])


@router.get("/{locataire_id}/paiements", response_model=LocatairePaiementOverviewResponse)
def get_locataire_paiements(locataire_id: int, db: Session = Depends(get_db)):
    service = LocatairePaiementService(db)
    overview = service.get_payment_overview(locataire_id)
    if overview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Locataire avec ID {locataire_id} introuvable",
        )
    return overview


@router.post("/{locataire_id}/paiements", response_model=LocatairePaiementResponse, status_code=status.HTTP_201_CREATED)
def create_locataire_paiement(
    locataire_id: int,
    payment_data: LocatairePaiementCreate,
    db: Session = Depends(get_db),
):
    service = LocatairePaiementService(db)
    paiement = service.record_payment(locataire_id, payment_data)
    if paiement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Locataire, bail actif ou quittance introuvable pour ce paiement",
        )
    return paiement
