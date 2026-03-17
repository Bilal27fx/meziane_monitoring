"""
sci_schema.py - Schemas validation SCI

Description:
Schemas Pydantic pour création et lecture de SCI.
Validation des données entrantes/sortantes API.

Dépendances:
- pydantic

Utilisé par:
- api.sci_routes
- services.patrimoine_service
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class SCIBase(BaseModel):  # Schema de base SCI (champs communs)
    nom: str = Field(..., min_length=1, max_length=200, description="Nom de la SCI")
    forme_juridique: str = Field(default="SCI", max_length=50)
    siret: Optional[str] = Field(None, min_length=14, max_length=14)
    date_creation: Optional[date] = None
    capital: Optional[float] = Field(None, ge=0)
    siege_social: Optional[str] = None
    gerant_nom: Optional[str] = Field(None, max_length=200)
    gerant_prenom: Optional[str] = Field(None, max_length=200)


class SCICreate(SCIBase):  # Schema création SCI
    pass


class SCIUpdate(BaseModel):  # Schema mise à jour SCI (tous champs optionnels)
    nom: Optional[str] = Field(None, min_length=1, max_length=200)
    forme_juridique: Optional[str] = Field(None, max_length=50)
    siret: Optional[str] = Field(None, min_length=14, max_length=14)
    date_creation: Optional[date] = None
    capital: Optional[float] = Field(None, ge=0)
    siege_social: Optional[str] = None
    gerant_nom: Optional[str] = Field(None, max_length=200)
    gerant_prenom: Optional[str] = Field(None, max_length=200)


class SCIResponse(SCIBase):  # Schema réponse API avec ID
    id: int

    class Config:
        from_attributes = True
