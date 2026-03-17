"""
locataire_schema.py - Schemas validation Locataire

Description:
Schemas Pydantic pour creation et lecture de Locataires.
Validation des donnees API.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


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
    telephone: str = Field(..., min_length=6, max_length=20)
    date_naissance: date
    profession: str = Field(..., min_length=1, max_length=200)
    revenus_annuels: float = Field(..., ge=0)


class LocataireUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    telephone: Optional[str] = Field(None, max_length=20)
    date_naissance: Optional[date] = None
    profession: Optional[str] = Field(None, max_length=200)
    revenus_annuels: Optional[float] = Field(None, ge=0)


class LocataireResponse(LocataireBase):
    id: int

    class Config:
        from_attributes = True
