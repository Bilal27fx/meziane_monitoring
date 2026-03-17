"""
dashboard_schema.py - Schemas validation Dashboard

Description:
Schemas Pydantic pour réponses API dashboard Bloomberg.
Validation structure KPI, cashflow, patrimoine, transactions, biens, etc.

Dépendances:
- pydantic

Utilisé par:
- api.dashboard_routes
- services.dashboard_service
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


# === KPI ===

class KPIResponse(BaseModel):
    """Schema réponse KPI principaux du dashboard"""
    patrimoine_net: float = Field(..., description="Patrimoine net total en euros")
    cashflow_today: float = Field(..., description="Cashflow cumulé du mois en cours")
    nb_alertes: int = Field(..., description="Nombre d'alertes actives")
    performance_ytd: float = Field(..., description="Performance année en cours (%)")
    taux_occupation: float = Field(..., description="Taux d'occupation des biens (%)")
    nb_locataires_actifs: int = Field(..., description="Nombre de locataires actifs")


# === CASHFLOW ===

class CashflowDayData(BaseModel):
    """Données cashflow pour un jour"""
    date: str = Field(..., description="Date au format ISO (YYYY-MM-DD)")
    revenus: float = Field(..., description="Revenus du jour")
    depenses: float = Field(..., description="Dépenses du jour")
    net: float = Field(..., description="Cashflow net du jour")


class Cashflow30DaysResponse(BaseModel):
    """Réponse cashflow 30 derniers jours"""
    data: List[CashflowDayData]


# === PATRIMOINE ===

class PatrimoineMonthData(BaseModel):
    """Données patrimoine pour un mois"""
    date: str = Field(..., description="Mois au format YYYY-MM")
    valeur: float = Field(..., description="Valeur patrimoine en euros")


class Patrimoine12MonthsResponse(BaseModel):
    """Réponse évolution patrimoine 12 mois"""
    data: List[PatrimoineMonthData]


# === TRANSACTIONS ===

class TransactionDashboardItem(BaseModel):
    """Transaction pour affichage dashboard"""
    id: int
    date: str = Field(..., description="Date au format ISO")
    montant: float
    libelle: str
    categorie: Optional[str] = None
    sci_nom: Optional[str] = None
    bien_adresse: Optional[str] = None
    statut_validation: str


class RecentTransactionsResponse(BaseModel):
    """Réponse dernières transactions"""
    data: List[TransactionDashboardItem]


# === BIENS ===

class BienTopRentabiliteItem(BaseModel):
    """Bien avec rentabilité pour top 5"""
    id: int
    adresse: str
    ville: str
    type_bien: str
    valeur_actuelle: float
    rentabilite_brute: float = Field(..., description="Rentabilité brute en %")
    rentabilite_nette: float = Field(..., description="Rentabilité nette en %")
    cashflow_annuel: float


class TopBiensResponse(BaseModel):
    """Réponse top 5 biens par rentabilité"""
    data: List[BienTopRentabiliteItem]


# === SCI ===

class SCIOverviewItem(BaseModel):
    """Vue d'ensemble d'une SCI"""
    id: int
    nom: str
    siret: Optional[str] = None
    nb_biens: int
    valeur_patrimoniale: float
    cashflow_annuel: float
    revenus_annuels: float
    depenses_annuelles: float


class SCIOverviewResponse(BaseModel):
    """Réponse vue d'ensemble SCI"""
    data: List[SCIOverviewItem]


# === LOCATAIRES ===

class LocataireOverviewItem(BaseModel):
    """Locataire avec statut paiement"""
    id: int
    nom: str
    prenom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    bien_adresse: Optional[str] = None
    loyer_mensuel: float
    statut_paiement: str = Field(..., description="Statut dernière quittance")
    nb_impayes: int = Field(..., description="Nombre de loyers impayés")
    date_debut_bail: str


class LocatairesOverviewResponse(BaseModel):
    """Réponse vue d'ensemble locataires"""
    data: List[LocataireOverviewItem]


# === OPPORTUNITÉS ===

class OpportuniteOverviewItem(BaseModel):
    """Opportunité immobilière pour dashboard"""
    id: int
    titre: Optional[str] = None
    ville: str
    prix: float
    surface: Optional[float] = None
    prix_m2: Optional[float] = None
    nb_pieces: Optional[int] = None
    score_global: Optional[int] = Field(None, description="Score IA global (0-100)")
    rentabilite_brute: Optional[float] = None
    rentabilite_nette: Optional[float] = None
    source: str
    url_annonce: str
    date_detection: str
    statut: str


class OpportunitesOverviewResponse(BaseModel):
    """Réponse vue d'ensemble opportunités"""
    data: List[OpportuniteOverviewItem]


# === DASHBOARD COMPLET ===

class FullDashboardResponse(BaseModel):
    """Réponse complète dashboard avec toutes les données"""
    kpi: KPIResponse
    cashflow_30days: List[CashflowDayData]
    patrimoine_12months: List[PatrimoineMonthData]
    recent_transactions: List[TransactionDashboardItem]
    top_biens: List[BienTopRentabiliteItem]
    sci_overview: List[SCIOverviewItem]
    locataires: List[LocataireOverviewItem]
    opportunites: List[OpportuniteOverviewItem]

    class Config:
        from_attributes = True
