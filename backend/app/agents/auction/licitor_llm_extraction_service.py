"""
licitor_llm_extraction_service.py - Extraction LLM des données annonce Licitor

Description:
Envoie les sections brutes d'une page Licitor au LLM (OpenAI json_object mode)
et retourne un objet structuré validé par Pydantic. Ne fait aucune transformation
du texte — délègue entièrement l'interprétation au LLM.

Dependances:
- openai
- pydantic
- app.config.settings
- licitor_text_segmenter.LicitorPageSections

Utilise par:
- adapters/licitor.py (parse_listing_detail)
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ValidationError

from app.agents.auction.licitor_text_segmenter import LicitorPageSections
from app.config import settings

logger = logging.getLogger(__name__)

_EXTRACTION_MODEL = "gpt-4o-mini"
_EXTRACTION_TEMPERATURE = 0.0
_EXTRACTION_TIMEOUT = 30.0

_SYSTEM_PROMPT = """Tu es un extracteur de données d'annonces de ventes judiciaires françaises.
À partir des sections de texte brut fournies, extrais les informations dans le format JSON demandé.
Règles strictes :
- Ne devine pas les données absentes — utilise null si l'information n'est pas dans le texte.
- Dates en format ISO 8601 (YYYY-MM-DD), heures en "HH:MM".
- Surfaces en float (nombre décimal), prix en float sans symbole €.
- amenities : objet avec les clés cave, parking, box, jardin, ascenseur, balcon, terrasse — valeur true/false/null.
- Pour chaque lot, extrais toutes les informations disponibles dans le texte du lot.
- extras : liste des annexes non couvertes par amenities (ex: "débarras", "emplacement de voiture").
- occupancy_status : "libre", "occupe", ou null si non mentionné."""

_JSON_SCHEMA = """{
  "tribunal": "string ou null",
  "city": "string ou null",
  "auction_date": "YYYY-MM-DD ou null",
  "auction_time": "HH:MM ou null",
  "lots": [
    {
      "lot_number": "integer ou null",
      "type_bien": "STUDIO / APPARTEMENT / MAISON / PARKING / AUTRE ou null",
      "surface_m2": "float ou null",
      "surface_balcon_m2": "float ou null",
      "surface_terrasse_m2": "float ou null",
      "etage": "integer ou null",
      "nb_pieces": "integer ou null",
      "nb_chambres": "integer ou null",
      "description": "texte brut du lot",
      "amenities": {
        "cave": "bool ou null",
        "parking": "bool ou null",
        "box": "bool ou null",
        "jardin": "bool ou null",
        "ascenseur": "bool ou null",
        "balcon": "bool ou null",
        "terrasse": "bool ou null"
      },
      "mise_a_prix": "float ou null",
      "extras": ["string"]
    }
  ],
  "address": "string ou null",
  "postal_code": "string ou null",
  "visit_dates": ["string"],
  "visit_location": "string ou null",
  "occupancy_status": "libre / occupe ou null",
  "lawyer_name": "string ou null",
  "lawyer_phone": "string ou null"
}"""


class LicitorLotExtraction(BaseModel):
    lot_number: Optional[int] = None
    type_bien: Optional[str] = None
    surface_m2: Optional[float] = None
    surface_balcon_m2: Optional[float] = None
    surface_terrasse_m2: Optional[float] = None
    etage: Optional[int] = None
    nb_pieces: Optional[int] = None
    nb_chambres: Optional[int] = None
    description: str = ""
    amenities: Dict[str, Optional[bool]] = {}
    mise_a_prix: Optional[float] = None
    extras: List[str] = []


class LicitorPageExtraction(BaseModel):
    tribunal: Optional[str] = None
    city: Optional[str] = None
    auction_date: Optional[str] = None
    auction_time: Optional[str] = None
    lots: List[LicitorLotExtraction] = []
    address: Optional[str] = None
    postal_code: Optional[str] = None
    visit_dates: List[str] = []
    visit_location: Optional[str] = None
    occupancy_status: Optional[str] = None
    lawyer_name: Optional[str] = None
    lawyer_phone: Optional[str] = None


class LicitorLLMUnavailableError(RuntimeError):
    pass


def extract_page(sections: LicitorPageSections) -> LicitorPageExtraction:
    """Envoie les sections brutes au LLM et retourne les données structurées validées."""
    if not settings.OPENAI_API_KEY:
        raise LicitorLLMUnavailableError("OPENAI_API_KEY absente")

    prompt = _build_user_prompt(sections)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=_EXTRACTION_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=_EXTRACTION_TEMPERATURE,
            timeout=_EXTRACTION_TIMEOUT,
        )
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        return LicitorPageExtraction(**data)

    except ValidationError as exc:
        raise LicitorLLMUnavailableError(f"JSON LLM invalide: {exc}") from exc
    except Exception as exc:
        raise LicitorLLMUnavailableError(f"Erreur LLM extraction: {exc}") from exc


def _build_user_prompt(sections: LicitorPageSections) -> str:
    """Construit le prompt user avec les sections labellisées."""
    parts: list[str] = []

    if sections.header:
        parts.append(f"[HEADER]\n{sections.header}")

    if sections.auction_block and sections.auction_block != sections.header:
        parts.append(f"[ENCHÈRE]\n{sections.auction_block}")

    for i, lot in enumerate(sections.lots, start=1):
        parts.append(f"[LOT {i}]\n{lot}")

    if not sections.lots and sections.raw_text:
        parts.append(f"[TEXTE COMPLET]\n{sections.raw_text[:4000]}")

    if sections.address_block:
        parts.append(f"[ADRESSE]\n{sections.address_block}")

    if sections.visit_block:
        parts.append(f"[VISITE]\n{sections.visit_block}")

    if sections.lawyer_block:
        parts.append(f"[AVOCAT]\n{sections.lawyer_block}")

    body = "\n\n".join(parts)
    return (
        f"Extrais les données de cette annonce judiciaire en respectant ce schéma JSON :\n\n"
        f"{_JSON_SCHEMA}\n\n"
        f"---\n\n"
        f"{body}"
    )


def build_extraction_payload(
    sections: LicitorPageSections,
    extraction: LicitorPageExtraction,
    raw_response: str = "",
) -> dict[str, Any]:
    """Construit le payload à persister en DB pour audit et debug."""
    return {
        "raw_sections": {
            "header": sections.header,
            "auction_block": sections.auction_block,
            "lots": sections.lots,
            "address_block": sections.address_block,
            "visit_block": sections.visit_block,
            "lawyer_block": sections.lawyer_block,
        },
        "parsed_extraction": extraction.model_dump(),
        "llm_raw_response": raw_response,
        "extraction_model": _EXTRACTION_MODEL,
    }
