"""
banking_schema.py - Schemas validation Banking

Description:
Schemas Pydantic pour connexion bancaire et synchronisation.
Validation données Bridge API.

Dépendances:
- pydantic

Utilisé par:
- api.banking_routes
- connectors.banking_connector
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class BankAccount(BaseModel):  # Schema compte bancaire Bridge
    id: int
    name: str
    balance: float
    currency: str = "EUR"
    type: str
    status: str
    iban: Optional[str] = None


class BankAccountListResponse(BaseModel):  # Schema réponse liste comptes
    accounts: List[BankAccount]
    total: int


class ImportTransactionsRequest(BaseModel):  # Schema requête import transactions
    sci_id: int = Field(..., gt=0, description="ID de la SCI propriétaire")
    account_id: int = Field(..., gt=0, description="ID du compte bancaire Bridge")
    since: Optional[str] = Field(None, description="Date début (YYYY-MM-DD)")
    until: Optional[str] = Field(None, description="Date fin (YYYY-MM-DD)")


class ImportTransactionsResponse(BaseModel):  # Schema réponse import transactions
    imported: int
    duplicates: int
    errors: int
    total: int
    message: str


class SyncAccountRequest(BaseModel):  # Schema requête synchronisation compte
    account_id: int = Field(..., gt=0, description="ID du compte bancaire Bridge")


class SyncAccountResponse(BaseModel):  # Schema réponse synchronisation
    success: bool
    message: str


class BankListResponse(BaseModel):  # Schema réponse liste banques
    banks: List[dict]
    total: int


class CreateItemRequest(BaseModel):  # Schema requête création item Bridge
    bank_id: int = Field(..., gt=0, description="ID de la banque")
    redirect_url: str = Field(..., description="URL de redirection après connexion")


class CreateItemResponse(BaseModel):  # Schema réponse création item
    item_id: Optional[int] = None
    redirect_url: Optional[str] = None
    message: str
