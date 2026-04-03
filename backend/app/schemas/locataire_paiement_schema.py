"""
locataire_paiement_schema.py - Schemas Pydantic pour les paiements locataire
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.locataire_paiement import ModePaiement


class LocatairePaiementCreate(BaseModel):
    montant: float = Field(..., gt=0)
    date_paiement: date
    mode_paiement: ModePaiement = ModePaiement.VIREMENT
    quittance_id: Optional[int] = Field(None, gt=0)
    periode_key: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$")
    reference: Optional[str] = Field(None, max_length=120)
    note: Optional[str] = Field(None, max_length=500)


class LocatairePaiementResponse(BaseModel):
    id: int
    locataire_id: int
    bail_id: int
    quittance_id: Optional[int] = None
    date_paiement: date
    montant: float
    mode_paiement: ModePaiement
    reference: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LocatairePaiementMonthStatus(BaseModel):
    key: str
    label: str
    quittance_id: Optional[int] = None
    statut: str
    montant_du: float
    montant_paye: float
    solde: float
    date_paiement: Optional[date] = None


class LocatairePaiementYearSummary(BaseModel):
    annee: int
    total_du: float
    total_paye: float
    reste_a_payer: float
    mensualites_total: int
    mensualites_reglees: int
    mensualites_en_retard: int


class LocatairePaiementOverviewResponse(BaseModel):
    locataire_id: int
    bail_id: Optional[int] = None
    date_debut_bail: Optional[date] = None
    date_fin_bail: Optional[date] = None
    montant_mensuel: float = 0
    total_du: float = 0
    total_paye: float = 0
    reste_a_payer: float = 0
    mensualites_total: int = 0
    mensualites_reglees: int = 0
    mensualites_en_retard: int = 0
    paiements: List[LocatairePaiementResponse] = []
    derniers_mois: List[LocatairePaiementMonthStatus] = []
    historique_mensuel: List[LocatairePaiementMonthStatus] = []
    resume_annuel: List[LocatairePaiementYearSummary] = []
