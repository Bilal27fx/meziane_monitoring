"""
locataire_schema.py - Schemas validation Locataire

Description:
Schemas Pydantic pour creation et lecture de Locataires.
Validation des donnees API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class BailCreateData(BaseModel):  # Données bail à créer avec le locataire
    bien_id: int = Field(..., gt=0)
    date_debut: date
    date_fin: Optional[date] = None
    loyer_mensuel: float = Field(..., gt=0)
    charges_mensuelles: float = Field(default=0, ge=0)
    depot_garantie: Optional[float] = Field(None, ge=0)


class LocataireBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    telephone: Optional[str] = Field(None, max_length=20)
    date_naissance: Optional[date] = None
    profession: Optional[str] = Field(None, max_length=200)
    revenus_annuels: Optional[float] = Field(None, ge=0)


class LocataireCreate(LocataireBase):
    email: str = Field(..., min_length=3, max_length=200)
    bail: Optional[BailCreateData] = None  # Bail créé en même temps que le locataire


class LocataireUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    telephone: Optional[str] = Field(None, max_length=20)
    date_naissance: Optional[date] = None
    profession: Optional[str] = Field(None, max_length=200)
    revenus_annuels: Optional[float] = Field(None, ge=0)
    bail: Optional[BailCreateData] = None  # Met à jour ou crée le bail actif


class BailInfo(BaseModel):  # Résumé bail actif dans LocataireResponse
    id: int
    bien_id: int
    bien_adresse: Optional[str] = None
    loyer_mensuel: float
    charges_mensuelles: float
    depot_garantie: Optional[float] = None
    date_debut: date
    date_fin: Optional[date] = None
    statut: str

    class Config:
        from_attributes = True


class LocataireResponse(LocataireBase):
    id: int
    bien_id: Optional[int] = None          # ID du bien du bail actif
    bail: Optional[BailInfo] = None        # Bail actif
    statut_paiement: Optional[str] = None  # a_jour / retard / impaye
    jours_retard: Optional[int] = None

    class Config:
        from_attributes = True


class LocatairePaginatedResponse(BaseModel):  # Réponse paginée pour liste locataires
    items: list[LocataireResponse]
    total: int
    page: int
    per_page: int
    pages: int


class BailSummary(BaseModel):  # Résumé bail pour LocataireDetailResponse
    id: int
    bien_adresse: Optional[str] = None
    loyer_mensuel: float
    charges_mensuelles: Optional[float] = None
    date_debut: date
    date_fin: Optional[date] = None
    statut: str

    class Config:
        from_attributes = True


class QuittanceSummary(BaseModel):  # Résumé quittance pour LocataireDetailResponse
    id: int
    mois: int
    annee: int
    montant_total: float
    statut: str

    class Config:
        from_attributes = True


class LocataireDetailResponse(LocataireBase):  # Schema réponse détaillée — frontend dashboard
    id: int
    bail_actif: Optional[BailSummary] = None        # Bail en cours
    quittances_recentes: List[QuittanceSummary] = [] # 3 dernières quittances
    nb_impayes: int = 0

    class Config:
        from_attributes = True
