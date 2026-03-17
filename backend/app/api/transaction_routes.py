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
    TransactionCategorizeRequest,
    TransactionCategorizeResponse
)
from app.models.transaction import TransactionCategorie, StatutValidation
from app.services.transaction_service import TransactionService
from app.services.categorization_service import CategorizationService
from app.utils.db import get_db

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("/", response_model=List[TransactionResponse])
def get_all_transactions(
    sci_id: Optional[int] = Query(None, description="Filtrer par SCI"),
    bien_id: Optional[int] = Query(None, description="Filtrer par bien"),
    categorie: Optional[TransactionCategorie] = Query(None, description="Filtrer par catégorie"),
    date_debut: Optional[date] = Query(None, description="Date de début"),
    date_fin: Optional[date] = Query(None, description="Date de fin"),
    statut_validation: Optional[StatutValidation] = Query(None, description="Filtrer par statut validation"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de résultats"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):  # Récupère transactions avec filtres optionnels
    service = TransactionService(db)
    return service.get_all_transactions(
        sci_id=sci_id,
        bien_id=bien_id,
        categorie=categorie,
        date_debut=date_debut,
        date_fin=date_fin,
        statut_validation=statut_validation,
        limit=limit,
        offset=offset
    )


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
    validateur: str = Query(..., description="Nom du validateur"),
    db: Session = Depends(get_db)
):  # Valide transaction manuellement
    service = TransactionService(db)
    transaction = service.valider_transaction(transaction_id, validateur)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction avec ID {transaction_id} introuvable"
        )
    return transaction


@router.post("/{transaction_id}/rejeter", response_model=TransactionResponse)
def rejeter_transaction(
    transaction_id: int,
    validateur: str = Query(..., description="Nom du validateur"),
    db: Session = Depends(get_db)
):  # Rejette transaction
    service = TransactionService(db)
    transaction = service.rejeter_transaction(transaction_id, validateur)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction avec ID {transaction_id} introuvable"
        )
    return transaction


@router.get("/analytics/by-categorie")
def get_analytics_by_categorie(
    sci_id: Optional[int] = Query(None, description="Filtrer par SCI"),
    annee: Optional[int] = Query(None, description="Filtrer par année"),
    db: Session = Depends(get_db)
):  # Récupère totaux par catégorie
    service = TransactionService(db)
    return service.get_total_by_categorie(sci_id=sci_id, annee=annee)


@router.get("/analytics/mensuel/{sci_id}/{annee}")
def get_analytics_mensuel(
    sci_id: int,
    annee: int,
    db: Session = Depends(get_db)
):  # Récupère total mensuel pour une SCI
    service = TransactionService(db)
    return service.get_total_mensuel(sci_id=sci_id, annee=annee)


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
