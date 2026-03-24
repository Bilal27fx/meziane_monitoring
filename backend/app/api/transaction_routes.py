"""
transaction_routes.py - Routes API gestion Transactions

Description:
Endpoints CRUD pour les transactions bancaires.
Filtrage par SCI, bien, catégorie, dates.
Validation et analytics.

Dépendances:
- transaction_service.py
- schemas.transaction_schema

Utilisé par:
- main.py (inclusion router)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.schemas.transaction_schema import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionPaginatedResponse,
    TransactionCategorizeRequest,
    TransactionCategorizeResponse,
    AnalyticsCategorieResponse,
    AnalyticsMensuelResponse,
)
from app.models.transaction import TransactionCategorie, StatutValidation
from app.services.transaction_service import TransactionService
from app.services.categorization_service import CategorizationService
from app.utils.db import get_db
from app.utils.auth import get_current_user, CurrentUser

router = APIRouter(prefix="/api/transactions", tags=["Transactions"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=TransactionPaginatedResponse)
def get_all_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    sci_id: Optional[int] = Query(None),
    bien_id: Optional[int] = Query(None),
    categorie: Optional[TransactionCategorie] = Query(None),
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
    statut: Optional[str] = Query(None, description="Statut: valide, en_attente, rejete"),
    db: Session = Depends(get_db)
):  # Récupère transactions paginées avec filtres — retourne {items, total, page, per_page, pages}
    statut_validation = None
    if statut:
        try:
            statut_validation = StatutValidation(statut)
        except ValueError:
            pass
    service = TransactionService(db)
    limit = per_page
    offset = (page - 1) * per_page
    items = service.get_all_transactions(
        sci_id=sci_id, bien_id=bien_id, categorie=categorie,
        date_debut=date_debut, date_fin=date_fin,
        statut_validation=statut_validation, limit=limit, offset=offset,
    )
    total = service.count_all_transactions(
        sci_id=sci_id, bien_id=bien_id, categorie=categorie,
        date_debut=date_debut, date_fin=date_fin, statut_validation=statut_validation,
    )
    pages = max(1, (total + per_page - 1) // per_page)
    return TransactionPaginatedResponse(items=items, total=total, page=page, per_page=per_page, pages=pages)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):  # Récupère transaction par ID
    service = TransactionService(db)
    transaction = service.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction avec ID {transaction_id} introuvable"
        )
    return transaction


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionCreate, db: Session = Depends(get_db)):  # Crée nouvelle transaction
    service = TransactionService(db)

    # Vérifier doublons
    duplicates = service.detect_duplicates(transaction_data)
    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transaction similaire détectée (ID: {duplicates[0].id})"
        )

    return service.create_transaction(transaction_data)


@router.post("/bulk", response_model=List[TransactionResponse], status_code=status.HTTP_201_CREATED)
def create_bulk_transactions(
    transactions_data: List[TransactionCreate],
    db: Session = Depends(get_db)
):  # Crée plusieurs transactions en masse
    service = TransactionService(db)
    return service.create_bulk_transactions(transactions_data)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db)
):  # Met à jour transaction existante
    service = TransactionService(db)
    transaction = service.update_transaction(transaction_id, transaction_data)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction avec ID {transaction_id} introuvable"
        )
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):  # Supprime transaction par ID
    service = TransactionService(db)
    success = service.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction avec ID {transaction_id} introuvable"
        )
    return None


@router.post("/{transaction_id}/valider", response_model=TransactionResponse)
def valider_transaction(
    transaction_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):  # Valide transaction — validateur = user connecté (RFC-008)
    service = TransactionService(db)
    transaction = service.valider_transaction(transaction_id, str(current_user.id))
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction {transaction_id} introuvable")
    return transaction


@router.post("/{transaction_id}/rejeter", response_model=TransactionResponse)
def rejeter_transaction(
    transaction_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):  # Rejette transaction — validateur = user connecté (RFC-008)
    service = TransactionService(db)
    transaction = service.rejeter_transaction(transaction_id, str(current_user.id))
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction {transaction_id} introuvable")
    return transaction


@router.get("/analytics/by-categorie", response_model=AnalyticsCategorieResponse)
def get_analytics_by_categorie(
    sci_id: Optional[int] = Query(None, description="Filtrer par SCI"),
    annee: Optional[int] = Query(None, description="Filtrer par année"),
    db: Session = Depends(get_db)
):  # Récupère totaux par catégorie
    service = TransactionService(db)
    return {"totaux": service.get_total_by_categorie(sci_id=sci_id, annee=annee)}


@router.get("/analytics/mensuel/{sci_id}/{annee}", response_model=AnalyticsMensuelResponse)
def get_analytics_mensuel(
    sci_id: int,
    annee: int,
    db: Session = Depends(get_db)
):  # Récupère total mensuel pour une SCI
    service = TransactionService(db)
    data = service.get_total_mensuel(sci_id=sci_id, annee=annee)
    return {"sci_id": sci_id, "annee": annee, "mois": {str(k): v for k, v in data.items()}}


@router.post("/{transaction_id}/categorize", response_model=TransactionResponse)
def categorize_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):  # Catégorise transaction automatiquement via IA
    transaction_service = TransactionService(db)
    categorization_service = CategorizationService()

    # Récupère transaction
    transaction = transaction_service.get_transaction_by_id(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction avec ID {transaction_id} introuvable"
        )

    # Catégorise avec IA
    result = categorization_service.categorize_transaction(
        libelle=transaction.libelle,
        montant=transaction.montant
    )

    # Met à jour transaction
    from app.schemas.transaction_schema import TransactionUpdate
    update_data = TransactionUpdate(
        categorie=result["categorie"],
        categorie_confidence=result["confidence"]
    )

    updated_transaction = transaction_service.update_transaction(transaction_id, update_data)
    return updated_transaction
