"""
opportunite_schema.py - Schemas validation Opportunités

Description:
Schemas Pydantic pour opportunités immobilières détectées.
Validation données API agent prospection.

Dépendances:
- pydantic
- models.opportunite (enums)

Utilisé par:
- api.opportunite_routes
- agents.agent_prospection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class SourceAnnonce(str, Enum):  # Source annonce
    SELOGER = "seloger"
    PAP = "pap"
    LEBONCOIN = "leboncoin"
    BIENICI = "bienici"
    LOGIC_IMMO = "logic_immo"
    AUTRE = "autre"


class StatutOpportunite(str, Enum):  # Statut opportunité
    NOUVEAU = "nouveau"
    VU = "vu"
    CONTACTE = "contacte"
    VISITE_PROGRAMMEE = "visite_programmee"
    OFFRE_FAITE = "offre_faite"
    REJETE = "rejete"
    ACQUIS = "acquis"


class OpportuniteBase(BaseModel):  # Schema base opportunité
    url_annonce: str
    source: SourceAnnonce
    titre: Optional[str] = None
    prix: float
    surface: Optional[float] = None
    prix_m2: Optional[float] = None
    ville: str
    adresse: Optional[str] = None
    nb_pieces: Optional[int] = None
    description: Optional[str] = None


class OpportuniteResponse(OpportuniteBase):  # Schema réponse opportunité
    id: int
    loyer_estime: Optional[float] = None
    travaux_estimes: Optional[float] = None
    rentabilite_brute: Optional[float] = None
    rentabilite_nette: Optional[float] = None
    score_global: Optional[int] = None
    raison_score: Optional[str] = None
    date_detection: date
    statut: StatutOpportunite

    class Config:
        from_attributes = True


class OpportuniteUpdateStatut(BaseModel):  # Schema mise à jour statut
    statut: StatutOpportunite
    notes: Optional[str] = None


class AgentRunResponse(BaseModel):  # Schema réponse lancement agent
    status: str
    message: str
    resultats: dict


class OpportuniteStatsResponse(BaseModel):  # Schema stats opportunités
    total: int
    par_statut: dict
    par_ville: dict
    score_moyen: float
    meilleures_opportunites: List[OpportuniteResponse]
