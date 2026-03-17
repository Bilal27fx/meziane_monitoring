"""
cashflow_schema.py - Schemas validation Cashflow

Description:
Schemas Pydantic pour réponses cashflow et analytics.
Validation données API calculs financiers.

Dépendances:
- pydantic

Utilisé par:
- api.cashflow_routes
- services.cashflow_service
"""

from pydantic import BaseModel
from typing import Optional, Dict


class CashflowBase(BaseModel):  # Schema base cashflow
    revenus: float
    depenses: float
    cashflow_net: float


class BienCashflowResponse(CashflowBase):  # Schema réponse cashflow bien
    bien_id: int
    annee: Optional[int] = None
    mois: Optional[int] = None


class SCICashflowResponse(CashflowBase):  # Schema réponse cashflow SCI
    sci_id: int
    annee: Optional[int] = None
    mois: Optional[int] = None


class GlobalCashflowResponse(CashflowBase):  # Schema réponse cashflow global
    annee: Optional[int] = None
    mois: Optional[int] = None


class CashflowMensuelResponse(BaseModel):  # Schema réponse cashflow mensuel
    data: Dict[int, Dict[str, float]]


class DepensesCategorieResponse(BaseModel):  # Schema réponse dépenses par catégorie
    categories: Dict[str, float]
    total: float


class RentabiliteResponse(BaseModel):  # Schema réponse rentabilité bien
    bien_id: int
    annee: int
    revenus_annuels: float
    depenses_annuelles: float
    cashflow_net: float
    valeur_bien: float
    rentabilite_brute: float
    rentabilite_nette: float


class SCICashflowSummary(BaseModel):  # Schema summary SCI pour dashboard
    sci_id: int
    nom: str
    revenus: float
    depenses: float
    cashflow_net: float


class DashboardSummaryResponse(BaseModel):  # Schema réponse dashboard complet
    annee: int
    global_data: GlobalCashflowResponse = None
    mensuel: Dict[int, Dict[str, float]]
    nb_transactions: int
    par_sci: list[SCICashflowSummary]

    class Config:
        alias_generator = lambda x: x.replace('global_data', 'global')
