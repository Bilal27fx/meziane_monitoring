"""
auction_scoring_service.py - Scoring LLM des annonces judiciaires

Description:
Envoie les métadonnées d'un AuctionListing à GPT-4o-mini et persiste le score.
Appelé après normalisation dans le pipeline d'ingestion Licitor.

Dependances:
- openai
- models.auction_listing
- config.settings

Utilise par:
- services.auction_ingestion_service
- api.auction_agent_routes (rescoring manuel)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.auction_listing import AuctionListing

logger = logging.getLogger(__name__)

# Loyers moyens Île-de-France par tranche de code postal (€/m²/mois)
_LOYERS_IDF = {
    "75": 30.0,   # Paris intra-muros
    "92": 24.0,   # Hauts-de-Seine
    "93": 18.0,   # Seine-Saint-Denis
    "94": 20.0,   # Val-de-Marne
    "91": 17.0,   # Essonne
    "95": 16.0,   # Val-d'Oise
    "77": 15.0,   # Seine-et-Marne
    "78": 17.0,   # Yvelines
}

_LOYER_DEFAUT = 15.0  # €/m²/mois hors IDF


class AuctionScoringResult(BaseModel):  # Réponse LLM validée
    score_global: int
    score_localisation: int
    score_prix: int
    score_potentiel: int
    loyer_estime: float
    rentabilite_brute: float
    raison_score: str
    risques: list[str]
    recommandation: str


def _loyer_reference(postal_code: Optional[str], surface_m2: Optional[float]) -> float:
    """Estime le loyer mensuel de référence depuis le code postal et la surface."""
    if not surface_m2 or surface_m2 <= 0:
        return 0.0
    prefix = (postal_code or "")[:2]
    taux = _LOYERS_IDF.get(prefix, _LOYER_DEFAUT)
    return round(taux * surface_m2, 2)


def _build_prompt(listing: AuctionListing) -> str:
    loyer_ref = _loyer_reference(listing.postal_code, listing.surface_m2)
    occupation = listing.occupancy_status or "inconnu"
    surface = f"{listing.surface_m2}m²" if listing.surface_m2 else "inconnue"
    prix = f"{listing.reserve_price:,.0f}€" if listing.reserve_price else "inconnue"
    prix_m2 = (
        f"{listing.reserve_price / listing.surface_m2:,.0f}€/m²"
        if listing.reserve_price and listing.surface_m2
        else "inconnu"
    )
    details = json.dumps(listing.property_details or {}, ensure_ascii=False)
    composants = ", ".join(
        label
        for label, enabled in [
            ("ascenseur", listing.ascenseur),
            ("balcon", listing.balcon),
            ("terrasse", listing.terrasse),
            ("cave", listing.cave),
            ("parking", listing.parking),
            ("box", listing.box),
            ("jardin", listing.jardin),
        ]
        if enabled is True
    ) or "non renseignés"

    return f"""Tu es expert en investissement immobilier locatif en France.
Analyse cette annonce de vente judiciaire et retourne un scoring détaillé.

**Annonce :**
- Titre : {listing.title}
- Type : {listing.listing_type or 'inconnu'}
- Ville : {listing.city or 'inconnue'} ({listing.postal_code or '?'})
- Adresse : {listing.address or 'inconnue'}
- Surface : {surface}
- Pièces : {listing.nb_pieces or 'inconnues'}
- Chambres : {listing.nb_chambres or 'inconnues'}
- Etage : {listing.type_etage or listing.etage or 'inconnu'}
- Composants : {composants}
- Mise à prix : {prix}
- Prix/m² : {prix_m2}
- Occupation : {occupation}
- Détails structurés : {details}
- URL : {listing.source_url}

**Contexte marché :**
- Loyer de référence estimé pour cette zone : {loyer_ref}€/mois
- Décote occupation : -15% à -30% si bien occupé
- Frais judiciaires à prévoir : ~10% du prix d'adjudication
- Cible rentabilité brute : > 5%

**Ta mission :**
1. Estime le loyer mensuel réaliste
2. Calcule la rentabilité brute (loyer annuel / mise à prix)
3. Score chaque dimension (0-100)
4. Identifie les risques principaux
5. Donne une recommandation finale

Réponds UNIQUEMENT en JSON valide :
{{
    "score_global": <int 0-100>,
    "score_localisation": <int 0-100>,
    "score_prix": <int 0-100>,
    "score_potentiel": <int 0-100>,
    "loyer_estime": <float>,
    "rentabilite_brute": <float>,
    "raison_score": "<explication 2-3 phrases>",
    "risques": ["<risque1>", "<risque2>"],
    "recommandation": "<fort_potentiel|a_surveiller|rejeter>"
}}"""


def score_listing(listing: AuctionListing, db: Session) -> bool:
    """Score un listing via LLM et persiste le résultat. Retourne True si scoré."""
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY absente — scoring désactivé pour listing %s", listing.id)
        return False

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es expert en investissement immobilier locatif. Réponds uniquement en JSON valide.",
                },
                {"role": "user", "content": _build_prompt(listing)},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            timeout=20,
        )

        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        result = AuctionScoringResult(**data)

    except ValidationError as exc:
        logger.error("Scoring listing %s — réponse LLM invalide : %s", listing.id, exc)
        return False
    except Exception as exc:
        logger.error("Scoring listing %s — erreur : %s", listing.id, exc)
        return False

    listing.score_global = result.score_global
    listing.score_localisation = result.score_localisation
    listing.score_prix = result.score_prix
    listing.score_potentiel = result.score_potentiel
    listing.loyer_estime = result.loyer_estime
    listing.rentabilite_brute = result.rentabilite_brute
    listing.raison_score = result.raison_score
    listing.risques_llm = result.risques
    listing.recommandation = result.recommandation
    listing.scored_at = datetime.utcnow()

    db.flush()
    logger.info(
        "Listing %s scoré : %s/100 (%s)",
        listing.id,
        result.score_global,
        result.recommandation,
    )
    return True
