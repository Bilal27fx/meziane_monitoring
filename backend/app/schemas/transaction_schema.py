"""
transaction_schema.py - Schemas validation Transaction

Description:
Schemas Pydantic pour création et lecture de Transactions bancaires.
Validation données API avec enums catégorie et statut.

Dépendances:
- pydantic
- models.transaction (enums)

Utilisé par:
- api.transaction_routes
- services.transaction_service
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import date
from enum import Enum


class TransactionCategorie(str, Enum):  # Catégories transactions SCI
    LOYER = "loyer"
    CHARGES_COPRO = "charges_copro"
    TAXE_FONCIERE = "taxe_fonciere"
    TRAVAUX = "travaux"
    REMBOURSEMENT_CREDIT = "remboursement_credit"
    ASSURANCE = "assurance"
    HONORAIRES = "honoraires"
    FRAIS_BANCAIRES = "frais_bancaires"
    AUTRE = "autre"


class StatutValidation(str, Enum):  # Statut validation transaction
    EN_ATTENTE = "en_attente"
    VALIDE = "valide"
    REJETE = "rejete"


class TransactionBase(BaseModel):  # Schema de base Transaction (champs communs)
    date: date
    montant: float
    libelle: str = Field(..., min_length=1)
    compte_bancaire_id: str = Field(..., min_length=1, max_length=100)
    categorie: Optional[TransactionCategorie] = None
    categorie_confidence: Optional[float] = Field(None, ge=0, le=1)
    bien_id: Optional[int] = Field(None, gt=0)
    locataire_id: Optional[int] = Field(None, gt=0)


class TransactionCreate(TransactionBase):  # Schema création Transaction
    sci_id: int = Field(..., gt=0)


class TransactionUpdate(BaseModel):  # Schema mise à jour Transaction (tous champs optionnels)
    date: Optional[date] = None
    montant: Optional[float] = None
    libelle: Optional[str] = Field(None, min_length=1)
    compte_bancaire_id: Optional[str] = Field(None, min_length=1, max_length=100)
    categorie: Optional[TransactionCategorie] = None
    categorie_confidence: Optional[float] = Field(None, ge=0, le=1)
    bien_id: Optional[int] = Field(None, gt=0)
    locataire_id: Optional[int] = Field(None, gt=0)
    statut_validation: Optional[StatutValidation] = None


class TransactionResponse(TransactionBase):  # Schema réponse API avec ID et métadonnées
    id: int
    sci_id: int
    statut_validation: StatutValidation
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    created_at: date

    class Config:
        from_attributes = True


class TransactionCategorizeRequest(BaseModel):  # Schema pour demande de catégorisation IA
    transaction_id: int = Field(..., gt=0)


class TransactionCategorizeResponse(BaseModel):  # Schema réponse catégorisation IA
    transaction_id: int
    categorie: TransactionCategorie
    confidence: float = Field(..., ge=0, le=1)
    raison: str


class AnalyticsCategorieResponse(BaseModel):  # Schema réponse analytics par catégorie
    totaux: Dict[str, float]


class AnalyticsMensuelItem(BaseModel):  # Un mois dans l'analytique mensuelle
    mois: int
    revenus: float
    depenses: float
    net: float


class AnalyticsMensuelResponse(BaseModel):  # Schema réponse analytics mensuelle
    sci_id: int
    annee: int
    mois: Dict[str, AnalyticsMensuelItem]
