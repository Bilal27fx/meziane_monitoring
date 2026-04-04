"""
quittance_schema.py - Schemas Pydantic pour les Quittances

Mappe le modèle Quittance (bail_id, mois int, annee int, montant_total)
vers la réponse attendue par le frontend (locataire_id, mois string, montant).
"""

from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import date
import locale


MOIS_FR = [
    "", "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"
]

STATUT_MAP = {
    "paye": "payee",
    "impaye": "impayee",
    "en_attente": "en_attente",
    "partiel": "en_attente",
}


class QuittanceResponse(BaseModel):
    id: int
    locataire_id: int
    mois: str
    montant: float
    montant_loyer: float = 0
    montant_charges: float = 0
    statut: str
    date_paiement: Optional[date] = None
    created_at: str = ""

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def build_from_orm(cls, obj):
        if not hasattr(obj, "bail"):
            return obj
        bail = obj.bail
        mois_int = obj.mois if isinstance(obj.mois, int) else 0
        annee_int = obj.annee if isinstance(obj.annee, int) else 0
        mois_label = f"{MOIS_FR[mois_int]} {annee_int}" if 1 <= mois_int <= 12 else f"{mois_int}/{annee_int}"
        statut_raw = obj.statut.value if hasattr(obj.statut, "value") else str(obj.statut)
        return {
            "id": obj.id,
            "locataire_id": bail.locataire_id if bail else 0,
            "mois": mois_label,
            "montant": obj.montant_total,
            "montant_loyer": float(obj.montant_loyer or 0),
            "montant_charges": float(obj.montant_charges or 0),
            "statut": STATUT_MAP.get(statut_raw, statut_raw),
            "date_paiement": obj.date_paiement,
            "created_at": "",
        }


class QuittanceGenerateResponse(BaseModel):
    message: str
    quittance_id: int
