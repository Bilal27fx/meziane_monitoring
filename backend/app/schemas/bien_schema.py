"""
bien_schema.py - Schemas validation Bien immobilier

Description:
Schemas Pydantic pour création et lecture de Biens.
Validation données API avec types enum.

Dépendances:
- pydantic
- models.bien (enums)

Utilisé par:
- api.bien_routes
- services.patrimoine_service
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from app.models.bien import TypeBien, StatutBien, ClasseDPE


class BienBase(BaseModel):  # Schema de base Bien (champs communs)
    sci_id: int = Field(..., gt=0)
    adresse: str = Field(..., min_length=1)
    ville: str = Field(..., min_length=1, max_length=100)
    code_postal: str = Field(..., min_length=5, max_length=5)
    complement_adresse: Optional[str] = Field(None, max_length=200)
    type_bien: TypeBien
    surface: Optional[float] = Field(None, gt=0)
    nb_pieces: Optional[int] = Field(None, gt=0)
    etage: Optional[int] = None
    date_acquisition: Optional[date] = None
    prix_acquisition: Optional[float] = Field(None, gt=0)
    valeur_actuelle: Optional[float] = Field(None, gt=0)
    dpe_classe: Optional[ClasseDPE] = None
    dpe_date_validite: Optional[date] = None
    statut: StatutBien = Field(default=StatutBien.VACANT)


class BienCreate(BienBase):  # Schema création Bien
    pass


class BienUpdate(BaseModel):  # Schema mise à jour Bien (tous champs optionnels)
    sci_id: Optional[int] = Field(None, gt=0)
    adresse: Optional[str] = Field(None, min_length=1)
    ville: Optional[str] = Field(None, min_length=1, max_length=100)
    code_postal: Optional[str] = Field(None, min_length=5, max_length=5)
    complement_adresse: Optional[str] = Field(None, max_length=200)
    type_bien: Optional[TypeBien] = None
    surface: Optional[float] = Field(None, gt=0)
    nb_pieces: Optional[int] = Field(None, gt=0)
    etage: Optional[int] = None
    date_acquisition: Optional[date] = None
    prix_acquisition: Optional[float] = Field(None, gt=0)
    valeur_actuelle: Optional[float] = Field(None, gt=0)
    dpe_classe: Optional[ClasseDPE] = None
    dpe_date_validite: Optional[date] = None
    statut: Optional[StatutBien] = None


class BienResponse(BienBase):  # Schema réponse API avec ID
    id: int

    class Config:
        from_attributes = True
