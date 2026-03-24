"""
quittance_routes.py - Routes API Quittances

Endpoints:
- GET  /api/locataires/{locataire_id}/quittances   liste des quittances d'un locataire
- POST /api/locataires/{locataire_id}/quittances/generer  génère la quittance du mois courant
- GET  /api/quittances/{id}/pdf                    téléchargement PDF (URL de stockage)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import date

from app.models.quittance import Quittance, StatutQuittance
from app.models.bail import Bail, StatutBail
from app.models.locataire import Locataire
from app.schemas.quittance_schema import QuittanceResponse, QuittanceGenerateResponse
from app.utils.db import get_db
from app.utils.auth import get_current_user

router = APIRouter(tags=["Quittances"], dependencies=[Depends(get_current_user)])


@router.get(
    "/api/locataires/{locataire_id}/quittances",
    response_model=List[QuittanceResponse],
)
def get_quittances_locataire(locataire_id: int, db: Session = Depends(get_db)):
    """Liste toutes les quittances d'un locataire, triées par date décroissante."""
    locataire = db.query(Locataire).filter(Locataire.id == locataire_id).first()
    if not locataire:
        raise HTTPException(status_code=404, detail=f"Locataire {locataire_id} introuvable")

    quittances = (
        db.query(Quittance)
        .join(Bail, Bail.id == Quittance.bail_id)
        .filter(Bail.locataire_id == locataire_id)
        .options(joinedload(Quittance.bail))
        .order_by(Quittance.annee.desc(), Quittance.mois.desc())
        .all()
    )
    return quittances


@router.post(
    "/api/locataires/{locataire_id}/quittances/generer",
    response_model=QuittanceGenerateResponse,
    status_code=status.HTTP_201_CREATED,
)
def generer_quittance(locataire_id: int, db: Session = Depends(get_db)):
    """Génère la quittance du mois courant pour le bail actif du locataire."""
    bail_actif = (
        db.query(Bail)
        .filter(Bail.locataire_id == locataire_id, Bail.statut == StatutBail.ACTIF)
        .first()
    )
    if not bail_actif:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun bail actif pour le locataire {locataire_id}"
        )

    today = date.today()
    mois, annee = today.month, today.year

    # Vérifier si la quittance du mois existe déjà
    existante = (
        db.query(Quittance)
        .filter(
            Quittance.bail_id == bail_actif.id,
            Quittance.mois == mois,
            Quittance.annee == annee,
        )
        .first()
    )
    if existante:
        raise HTTPException(
            status_code=409,
            detail=f"Quittance {mois}/{annee} déjà générée (ID: {existante.id})"
        )

    montant_total = bail_actif.loyer_mensuel + bail_actif.charges_mensuelles
    quittance = Quittance(
        bail_id=bail_actif.id,
        mois=mois,
        annee=annee,
        montant_loyer=bail_actif.loyer_mensuel,
        montant_charges=bail_actif.charges_mensuelles,
        montant_total=montant_total,
        statut=StatutQuittance.EN_ATTENTE,
    )
    db.add(quittance)
    db.commit()
    db.refresh(quittance)

    return QuittanceGenerateResponse(
        message=f"Quittance {mois}/{annee} générée",
        quittance_id=quittance.id,
    )


@router.get("/api/quittances/{quittance_id}/pdf")
def get_quittance_pdf(quittance_id: int, db: Session = Depends(get_db)):
    """Retourne l'URL du PDF de la quittance (redirect vers MinIO/stockage)."""
    quittance = db.query(Quittance).filter(Quittance.id == quittance_id).first()
    if not quittance:
        raise HTTPException(status_code=404, detail=f"Quittance {quittance_id} introuvable")

    if not quittance.fichier_url:
        raise HTTPException(
            status_code=404,
            detail="Aucun PDF généré pour cette quittance"
        )

    return RedirectResponse(url=quittance.fichier_url)
