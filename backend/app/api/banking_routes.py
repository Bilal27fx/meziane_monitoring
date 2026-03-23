"""
banking_routes.py - Routes API connexion bancaire

Description:
Endpoints pour connexion banques via Bridge API.
Liste banques, comptes, import transactions, synchronisation.

Dépendances:
- banking_connector.py
- schemas.banking_schema

Utilisé par:
- main.py (inclusion router)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.banking_schema import (
    BankAccountListResponse,
    ImportTransactionsRequest,
    ImportTransactionsResponse,
    SyncAccountRequest,
    SyncAccountResponse,
    BankListResponse,
    CreateItemRequest,
    CreateItemResponse
)
from app.connectors.banking_connector import BankingConnectorService
from app.utils.db import get_db
from app.utils.logger import setup_logger
from app.utils.auth import get_current_user

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/banking", tags=["Banking"], dependencies=[Depends(get_current_user)])


@router.get("/banks", response_model=BankListResponse)
async def list_banks():  # Liste toutes les banques supportées par Bridge
    connector = BankingConnectorService()

    if not await connector.authenticate():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Impossible de se connecter à Bridge API"
        )

    banks = await connector.list_banks()
    return {"banks": banks, "total": len(banks)}


@router.get("/accounts/{user_uuid}")
async def list_user_accounts(user_uuid: str):  # Liste comptes bancaires utilisateur Bridge
    connector = BankingConnectorService()

    if not await connector.authenticate():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Impossible de se connecter à Bridge API"
        )

    accounts = await connector.get_user_accounts(user_uuid)
    return {"accounts": accounts, "total": len(accounts)}


@router.post("/import", response_model=ImportTransactionsResponse)
async def import_transactions(
    request: ImportTransactionsRequest,
    db: Session = Depends(get_db)
):  # Importe transactions bancaires depuis Bridge vers DB
    connector = BankingConnectorService()

    if not await connector.authenticate():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Impossible de se connecter à Bridge API"
        )

    try:
        result = await connector.import_transactions_to_db(
            sci_id=request.sci_id,
            account_id=request.account_id,
            db_session=db,
            since=request.since,
            until=request.until
        )
        return {**result, "message": f"{result['imported']} transactions importées avec succès"}

    except Exception as e:
        logger.error(f"Erreur import transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'import: {str(e)}"
        )


@router.post("/sync", response_model=SyncAccountResponse)
async def sync_account(request: SyncAccountRequest):  # Déclenche synchronisation compte bancaire
    connector = BankingConnectorService()

    if not await connector.authenticate():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Impossible de se connecter à Bridge API"
        )

    success = await connector.sync_account(request.account_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de la synchronisation"
        )

    return {"success": True, "message": f"Synchronisation du compte {request.account_id} déclenchée"}


@router.post("/items", response_model=CreateItemResponse)
async def create_item(request: CreateItemRequest):  # Crée item Bridge pour connexion banque
    connector = BankingConnectorService()

    if not await connector.authenticate():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Impossible de se connecter à Bridge API"
        )

    result = await connector.create_item(bank_id=request.bank_id, redirect_url=request.redirect_url)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de l'item"
        )

    return {"item_id": result.get("id"), "redirect_url": result.get("redirect_url"), "message": "Item créé avec succès"}


@router.get("/transactions/{account_id}")
async def get_account_transactions(
    account_id: int,
    since: str = None,
    until: str = None,
    limit: int = 100
):  # Récupère transactions brutes Bridge (sans import DB)
    connector = BankingConnectorService()

    if not await connector.authenticate():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Impossible de se connecter à Bridge API"
        )

    transactions = await connector.get_account_transactions(
        account_id=account_id,
        since=since,
        until=until,
        limit=limit
    )
    return {"transactions": transactions, "total": len(transactions)}
