"""
auction_scoring_service.py - Scoring hybride des annonces judiciaires

Description:
Calcule une base déterministe orientée petits biens à Paris, puis utilise
éventuellement le LLM pour quelques signaux qualitatifs bornés.
"""

from __future__ import annotations

import logging
from datetime import datetime
import json
from typing import Any, Optional

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
_FRAIS_ADJUDICATION_RATIO = 0.10

_REFERENCE_PRICE_M2 = {
    "75": 11000.0,
    "92": 7600.0,
    "93": 4200.0,
    "94": 5200.0,
    "91": 3400.0,
    "95": 3100.0,
    "77": 2900.0,
    "78": 4300.0,
}

_PREMIUM_NEAR_PARIS = {
    "boulogne-billancourt",
    "neuilly-sur-seine",
    "levallois-perret",
    "vincennes",
    "issy-les-moulineaux",
    "montrouge",
    "saint-mande",
    "clichy",
}


class AuctionQualitativeSignals(BaseModel):
    micro_localisation_bonus: int = 0
    qualite_bien_bonus: int = 0
    travaux_estimes: float = 0.0
    raison_score: str
    risques: list[str]


class AuctionScoringBreakdown(BaseModel):
    score_global: int
    score_localisation: int
    score_prix: int
    score_potentiel: int
    score_cible_paris_petite_surface: int
    score_liquidite: int
    score_occupation: int
    score_qualite_bien: int
    bonus_strategique: int
    categorie_investissement: str
    loyer_estime: float
    rentabilite_brute: float
    travaux_estimes: float
    valeur_marche_estimee: float
    valeur_marche_ajustee: float
    prix_max_cible: float
    prix_max_agressif: float
    raison_score: str
    risques: list[str]
    recommandation: str


class AuctionLLMUnavailableError(RuntimeError):
    pass


def _loyer_reference(postal_code: Optional[str], surface_m2: Optional[float]) -> float:
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
    audience = listing.auction_date.strftime("%d/%m/%Y %H:%M") if listing.auction_date else "inconnue"
    lieu_audience = listing.auction_location or listing.auction_tribunal or "inconnu"
    visite = (listing.visit_dates or ["inconnue"])[0]
    categorie_actuelle = listing.categorie_investissement or "non calculée"

    return f"""Tu travailles comme agent immobilier professionnel spécialisé en ventes judiciaires immobilières en France.
Ta mission est de détecter avant tout le monde les vraies opportunités en or, tout en restant lucide sur les pièges classiques des enchères.

Tu ne joues pas un rôle générique de conseiller immobilier.
Tu raisonnes comme un professionnel du marché qui:
- cherche des biens sous-valorisés avant la concurrence
- privilégie la liquidité, la revente et le potentiel locatif réel
- valorise fortement les petites surfaces à Paris et les micro-localisations tendues
- pénalise sévèrement les biens complexes, peu liquides, occupés ou juridiquement flous
- reste discipliné: pas d'enthousiasme artificiel, pas d'invention, pas de score global libre

Le score global final est calculé par le système.
Tu fournis uniquement des signaux qualitatifs bornés qui améliorent la précision du scoring déterministe.

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
- Audience : {audience}
- Lieu audience : {lieu_audience}
- Première visite : {visite}
- Détails structurés : {details}
- URL : {listing.source_url}

**Contexte métier :**
- Il s'agit d'un agent qui doit faire remonter rapidement les meilleures ventes judiciaires avant qu'elles soient travaillées par d'autres investisseurs.
- On veut capter les opportunités les plus actionnables, pas faire une expertise notariale complète.
- Une annonce peut sembler bon marché mais être médiocre si la sortie est lente, l'occupation mauvaise ou le quartier peu liquide.
- Inversement, un petit bien très liquide dans une bonne zone peut mériter un bonus fort même si le texte source est imparfait.

**Contexte d'investissement :**
- Loyer de référence estimé pour cette zone : {loyer_ref}€/mois
- Décote occupation : -15% à -30% si bien occupé
- Frais judiciaires à prévoir : ~10% du prix d'adjudication
- Stratégie cible : prioriser petits biens à Paris, surtout 9 à 35m²
- Cœur de cible absolu : 18 à 25m²
- Catégorie actuelle calculée par le système : {categorie_actuelle}

**Contraintes de réponse**
- `micro_localisation_bonus` doit être un entier entre -10 et 10
- `qualite_bien_bonus` doit être un entier entre -10 et 10
- `travaux_estimes` doit rester prudent et réaliste
- Ne pas recalculer de score global
- N'invente pas de données absentes
- Si l'information est insuffisante, reste modéré plutôt que spéculatif
- Les bonus doivent être rares et mérités
- Les malus doivent être francs si la liquidité ou la sortie semblent mauvaises

**Ta mission :**
1. Estime un bonus/malus de micro-localisation en te demandant si un investisseur réactif voudrait vraiment se positionner vite
2. Estime un bonus/malus de qualité intrinsèque du bien pour la location et la revente
3. Estime les travaux seulement s'il existe de vrais signaux de défaut ou d'obsolescence
4. Rédige une synthèse courte orientée décision, comme pour un investisseur professionnel
5. Liste les risques principaux qui peuvent détruire la valeur ou la vitesse de sortie

**Repères d'analyse**
- Bonus micro-localisation: zone très recherchée, excellente desserte, quartier liquide, adresse crédible pour petite surface
- Malus micro-localisation: marché lent, desserte faible, commune peu demandée, revente ou relocation difficiles
- Bonus qualité: plan efficace, étage correct, ascenseur si étage élevé, balcon/terrasse, cave, bon état, luminosité
- Malus qualité: RDC pénalisant, gros travaux, distribution faible, bien atypique, nuisances probables
- Travaux: reste crédible et conservateur, ne gonfle pas sans signal texte réel

Réponds UNIQUEMENT en JSON valide :
{{
    "micro_localisation_bonus": <int -10..10>,
    "qualite_bien_bonus": <int -10..10>,
    "travaux_estimes": <float>,
    "raison_score": "<explication 2-3 phrases>",
    "risques": ["<risque1>", "<risque2>"]
}}"""

def _clip(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _round_int(value: float) -> int:
    return int(round(_clip(value, 0, 100)))


def _city_slug(listing: AuctionListing) -> str:
    return (listing.city or "").strip().lower()


def _is_paris(listing: AuctionListing) -> bool:
    postal_code = listing.postal_code or ""
    city = _city_slug(listing)
    return postal_code.startswith("75") or city.startswith("paris")


def _is_premium_near_paris(listing: AuctionListing) -> bool:
    return _city_slug(listing) in _PREMIUM_NEAR_PARIS


def _extract_typology(listing: AuctionListing) -> str:
    raw_typology = str((listing.property_details or {}).get("typology") or "").upper()
    if raw_typology in {"STUDIO", "T1", "T2", "T3", "T4", "T5", "F1", "F2", "F3", "F4", "F5"}:
        return raw_typology

    if listing.nb_pieces:
        return f"T{listing.nb_pieces}"

    if listing.surface_m2 and listing.surface_m2 <= 18:
        return "STUDIO"
    if listing.surface_m2 and listing.surface_m2 <= 35:
        return "T2"
    if listing.surface_m2 and listing.surface_m2 <= 55:
        return "T3"
    return "APPARTEMENT"


def _score_localisation(listing: AuctionListing, micro_bonus: int) -> int:
    postal_prefix = (listing.postal_code or "")[:2]
    if _is_paris(listing):
        base = 100
    elif _is_premium_near_paris(listing):
        base = 82
    elif postal_prefix in {"92", "93", "94"}:
        base = 64
    elif postal_prefix in {"77", "78", "91", "95"}:
        base = 42
    else:
        base = 28
    return _round_int(base + micro_bonus)


def _score_typologie(listing: AuctionListing) -> int:
    typology = _extract_typology(listing)
    if typology in {"STUDIO", "T1", "F1", "T2", "F2"}:
        return 100
    if typology in {"T3", "F3"}:
        return 60
    if typology in {"T4", "F4", "T5", "F5"}:
        return 20
    if listing.surface_m2 and listing.surface_m2 <= 35:
        return 85
    return 40


def _score_surface(surface_m2: float | None) -> int:
    if not surface_m2 or surface_m2 <= 0:
        return 20
    if surface_m2 < 9:
        return 10
    if surface_m2 <= 18:
        return 90
    if surface_m2 <= 25:
        return 100
    if surface_m2 <= 35:
        return 86
    if surface_m2 <= 45:
        return 60
    return 20


def _weighted_score(items: list[tuple[int, float]]) -> int:
    total_weight = sum(weight for _, weight in items)
    weighted_sum = sum(score * weight for score, weight in items)
    return _round_int(weighted_sum / total_weight) if total_weight else 0


def _estimate_travaux(listing: AuctionListing, llm_estimate: float) -> float:
    reserve_price = listing.reserve_price or 0.0
    details = listing.property_details or {}
    condition_signals = set(details.get("condition_signals") or [])
    if llm_estimate > 0:
        return round(llm_estimate, 2)
    if "a_renover" in condition_signals:
        return round(max(12000.0, reserve_price * 0.08), 2)
    if "a_rafraichir" in condition_signals:
        return round(max(6000.0, reserve_price * 0.04), 2)
    if "refait_a_neuf" in condition_signals or "bon_etat" in condition_signals:
        return round(max(0.0, reserve_price * 0.01), 2)
    return round(max(2500.0 if reserve_price else 0.0, reserve_price * 0.02), 2)


def _reference_price_m2(listing: AuctionListing) -> float:
    prefix = (listing.postal_code or "")[:2]
    return _REFERENCE_PRICE_M2.get(prefix, 2500.0)


def _market_values(listing: AuctionListing, travaux_estimes: float) -> tuple[float, float, float]:
    reserve_price = listing.reserve_price or 0.0
    surface_m2 = listing.surface_m2 or 0.0
    reference_price_m2 = _reference_price_m2(listing)
    valeur_marche_estimee = round(reference_price_m2 * surface_m2, 2) if surface_m2 else round(reserve_price * 1.15, 2)
    coeff_occupation = 0.78 if (listing.occupancy_status or "").lower() == "occupe" else 1.0
    valeur_marche_ajustee = round(valeur_marche_estimee * coeff_occupation, 2)
    cout_total = round(reserve_price * (1 + _FRAIS_ADJUDICATION_RATIO) + travaux_estimes, 2)
    return valeur_marche_estimee, valeur_marche_ajustee, cout_total


def _score_ratio(ratio: float | None) -> int:
    if ratio is None:
        return 25
    if ratio <= 0.70:
        return 100
    if ratio <= 0.78:
        return 88
    if ratio <= 0.85:
        return 67
    if ratio <= 0.92:
        return 40
    return 15


def _score_price_block(listing: AuctionListing, travaux_estimes: float) -> tuple[int, float, float]:
    valeur_marche_estimee, valeur_marche_ajustee, cout_total = _market_values(listing, travaux_estimes)
    reserve_price = listing.reserve_price or 0.0
    surface_m2 = listing.surface_m2 or 0.0
    reference_price_m2 = _reference_price_m2(listing)

    start_ratio = reserve_price / valeur_marche_ajustee if reserve_price and valeur_marche_ajustee else None
    target_ratio = cout_total / valeur_marche_ajustee if cout_total and valeur_marche_ajustee else None
    price_m2 = reserve_price / surface_m2 if reserve_price and surface_m2 else None
    relative_m2 = price_m2 / reference_price_m2 if price_m2 and reference_price_m2 else None

    start_score = _score_ratio(start_ratio)
    target_score = _score_ratio(target_ratio)
    if relative_m2 is None:
        price_m2_score = 30
    elif relative_m2 <= 0.70:
        price_m2_score = 100
    elif relative_m2 <= 0.82:
        price_m2_score = 85
    elif relative_m2 <= 0.95:
        price_m2_score = 62
    else:
        price_m2_score = 22

    score_prix = _weighted_score([(start_score, 5), (target_score, 15), (price_m2_score, 5)])
    return score_prix, valeur_marche_estimee, valeur_marche_ajustee


def _score_liquidite(listing: AuctionListing, micro_bonus: int) -> int:
    typology_score = _score_typologie(listing)
    surface_score = _score_surface(listing.surface_m2)
    location_score = _score_localisation(listing, micro_bonus)

    if _is_paris(listing):
        tension = 98
        transport = 95
    elif _is_premium_near_paris(listing):
        tension = 84
        transport = 88
    elif (listing.postal_code or "")[:2] in {"92", "93", "94"}:
        tension = 70
        transport = 74
    else:
        tension = 48
        transport = 46

    liquidite_revente = _weighted_score([(typology_score, 0.45), (surface_score, 0.35), (location_score, 0.20)])
    return _weighted_score([(tension, 8), (liquidite_revente, 6), (transport, 6)])


def _score_occupation(listing: AuctionListing) -> int:
    occupancy = (listing.occupancy_status or "").lower()
    if occupancy == "libre":
        free_score = 100
        risk_score = 95
    elif occupancy == "occupe":
        free_score = 30
        risk_score = 25
    else:
        free_score = 45
        risk_score = 45
    return _weighted_score([(free_score, 10), (risk_score, 5)])


def _score_qualite(listing: AuctionListing, quality_bonus: int) -> int:
    details = listing.property_details or {}
    positive = 0
    if listing.balcon or listing.terrasse or listing.jardin:
        positive += 1
    if listing.cave or listing.parking or listing.box:
        positive += 1
    if listing.etage is not None and listing.etage >= 1:
        positive += 1
    if listing.ascenseur and (listing.etage or 0) >= 3:
        positive += 1
    if "lumineux" in set(details.get("layout_signals") or []):
        positive += 1

    condition_signals = set(details.get("condition_signals") or [])
    negative = 0
    if "a_renover" in condition_signals:
        negative += 2
    elif "a_rafraichir" in condition_signals:
        negative += 1
    if listing.type_etage == "rez_de_chaussee":
        negative += 1

    base = 55 + positive * 9 - negative * 12
    return _round_int(base + quality_bonus)


def _bonus_strategique(listing: AuctionListing) -> int:
    typology = _extract_typology(listing)
    target_typology = typology in {"STUDIO", "T1", "F1", "T2", "F2"}
    surface_m2 = listing.surface_m2 or 0.0
    if _is_paris(listing) and target_typology and 18 <= surface_m2 <= 25:
        return 10
    if _is_paris(listing) and target_typology and 9 <= surface_m2 <= 35:
        return 7
    if _is_premium_near_paris(listing) and target_typology and 9 <= surface_m2 <= 35:
        return 4
    return 0


def _categorie_investissement(score_final: int) -> str:
    if score_final >= 85:
        return "opportunite_rare"
    if score_final >= 70:
        return "prioritaire"
    if score_final >= 55:
        return "a_etudier"
    return "hors_cible"


def _recommandation_from_category(category: str) -> str:
    if category in {"opportunite_rare", "prioritaire"}:
        return "fort_potentiel"
    if category == "a_etudier":
        return "a_surveiller"
    return "rejeter"


def _occupancy_discount_coefficient(listing: AuctionListing) -> float:
    return 0.78 if (listing.occupancy_status or "").lower() == "occupe" else 1.0


def _prix_max(valeur_marche_estimee: float, listing: AuctionListing, travaux_estimes: float, coefficient: float) -> float:
    valeur_ajustee = valeur_marche_estimee * _occupancy_discount_coefficient(listing)
    return round(max(0.0, valeur_ajustee * coefficient - travaux_estimes) / (1 + _FRAIS_ADJUDICATION_RATIO), 2)


def _fetch_qualitative_signals(listing: AuctionListing) -> AuctionQualitativeSignals:
    if not settings.OPENAI_API_KEY:
        raise AuctionLLMUnavailableError("OPENAI_API_KEY absente")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un agent immobilier professionnel expert des ventes judiciaires en France. "
                        "Tu repères les opportunités en or avant la concurrence, mais tu restes factuel, discipliné "
                        "et prudent sur les risques. Tu ne produis jamais de score global libre. "
                        "Tu réponds uniquement en JSON valide, sans texte additionnel."
                    ),
                },
                {"role": "user", "content": _build_prompt(listing)},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            timeout=20,
        )
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        result = AuctionQualitativeSignals(**data)
        result.micro_localisation_bonus = int(_clip(result.micro_localisation_bonus, -10, 10))
        result.qualite_bien_bonus = int(_clip(result.qualite_bien_bonus, -10, 10))
        result.travaux_estimes = max(0.0, result.travaux_estimes)
        return result
    except ValidationError as exc:
        raise AuctionLLMUnavailableError(f"Réponse qualitative LLM invalide: {exc}") from exc
    except Exception as exc:
        raise AuctionLLMUnavailableError(f"Erreur LLM qualitative: {exc}") from exc


def _compute_scoring(listing: AuctionListing, qualitative: AuctionQualitativeSignals) -> AuctionScoringBreakdown:
    loyer_estime = _loyer_reference(listing.postal_code, listing.surface_m2)
    travaux_estimes = _estimate_travaux(listing, qualitative.travaux_estimes)
    score_cible = _weighted_score(
        [
            (_score_localisation(listing, qualitative.micro_localisation_bonus), 15),
            (_score_typologie(listing), 10),
            (_score_surface(listing.surface_m2), 10),
        ]
    )
    score_prix, valeur_marche_estimee, valeur_marche_ajustee = _score_price_block(listing, travaux_estimes)
    score_liquidite = _score_liquidite(listing, qualitative.micro_localisation_bonus)
    score_occupation = _score_occupation(listing)
    score_qualite_bien = _score_qualite(listing, qualitative.qualite_bien_bonus)
    bonus_strategique = _bonus_strategique(listing)

    score_base = (
        score_cible * 0.35
        + score_prix * 0.25
        + score_liquidite * 0.20
        + score_occupation * 0.15
        + score_qualite_bien * 0.05
    )
    score_global = _round_int(min(100.0, score_base + bonus_strategique))
    categorie = _categorie_investissement(score_global)
    reserve_price = listing.reserve_price or 0.0
    rentabilite_brute = round(((loyer_estime * 12) / reserve_price) * 100, 2) if reserve_price > 0 and loyer_estime > 0 else 0.0

    return AuctionScoringBreakdown(
        score_global=score_global,
        score_localisation=score_cible,
        score_prix=score_prix,
        score_potentiel=score_liquidite,
        score_cible_paris_petite_surface=score_cible,
        score_liquidite=score_liquidite,
        score_occupation=score_occupation,
        score_qualite_bien=score_qualite_bien,
        bonus_strategique=bonus_strategique,
        categorie_investissement=categorie,
        loyer_estime=loyer_estime,
        rentabilite_brute=rentabilite_brute,
        travaux_estimes=travaux_estimes,
        valeur_marche_estimee=valeur_marche_estimee,
        valeur_marche_ajustee=valeur_marche_ajustee,
        prix_max_cible=_prix_max(valeur_marche_estimee, listing, travaux_estimes, 0.78),
        prix_max_agressif=_prix_max(valeur_marche_estimee, listing, travaux_estimes, 0.70),
        raison_score=qualitative.raison_score,
        risques=qualitative.risques,
        recommandation=_recommandation_from_category(categorie),
    )


def score_listing(listing: AuctionListing, db: Session) -> bool:
    try:
        qualitative = _fetch_qualitative_signals(listing)
    except AuctionLLMUnavailableError as exc:
        logger.error("Listing %s non scoré — LLM indisponible: %s", listing.id, exc)
        return False

    result = _compute_scoring(listing, qualitative)

    listing.score_global = result.score_global
    listing.score_localisation = result.score_localisation
    listing.score_prix = result.score_prix
    listing.score_potentiel = result.score_potentiel
    listing.score_cible_paris_petite_surface = result.score_cible_paris_petite_surface
    listing.score_liquidite = result.score_liquidite
    listing.score_occupation = result.score_occupation
    listing.score_qualite_bien = result.score_qualite_bien
    listing.bonus_strategique = result.bonus_strategique
    listing.categorie_investissement = result.categorie_investissement
    listing.loyer_estime = result.loyer_estime
    listing.rentabilite_brute = result.rentabilite_brute
    listing.travaux_estimes = result.travaux_estimes
    listing.valeur_marche_estimee = result.valeur_marche_estimee
    listing.valeur_marche_ajustee = result.valeur_marche_ajustee
    listing.prix_max_cible = result.prix_max_cible
    listing.prix_max_agressif = result.prix_max_agressif
    listing.raison_score = result.raison_score
    listing.risques_llm = result.risques
    listing.recommandation = result.recommandation
    listing.scored_at = datetime.utcnow()

    db.flush()
    logger.info("Listing %s scoré : %s/100 (%s)", listing.id, result.score_global, result.categorie_investissement)
    return True
