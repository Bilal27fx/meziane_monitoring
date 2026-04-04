"""
auction_scoring_service.py - Scoring hybride des annonces judiciaires

Description:
Calcule une base déterministe orientée petits biens à Paris, puis utilise
éventuellement le LLM pour quelques signaux qualitatifs bornés.
"""

from __future__ import annotations

import logging
from datetime import datetime
from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.auction_listing import AuctionListing

logger = logging.getLogger(__name__)

_SCORING_CONFIG_PATH = Path(__file__).with_name("auction_scoring_config.json")


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


@lru_cache(maxsize=1)
def _scoring_config() -> dict[str, Any]:
    with _SCORING_CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _market_config() -> dict[str, Any]:
    return _scoring_config()["market"]


def _llm_config() -> dict[str, Any]:
    return _scoring_config()["llm"]


def _scoring_rules() -> dict[str, Any]:
    return _scoring_config()["scoring"]


def _range_score(value: float | None, rules: list[dict[str, Any]], default_score: int) -> int:
    if value is None:
        return default_score
    for rule in rules:
        if value <= float(rule["max"]):
            return int(rule["score"])
    return default_score


def _loyer_reference(postal_code: Optional[str], surface_m2: Optional[float]) -> float:
    if not surface_m2 or surface_m2 <= 0:
        return 0.0
    prefix = (postal_code or "")[:2]
    market = _market_config()
    taux = float(market["loyers_idf"].get(prefix, market["loyer_defaut"]))
    return round(taux * surface_m2, 2)


def _build_prompt(listing: AuctionListing) -> str:
    llm = _llm_config()
    scoring = _scoring_rules()
    market = _market_config()
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
    return llm["user_prompt_template"].format(
        title=listing.title,
        listing_type=listing.listing_type or "inconnu",
        city=listing.city or "inconnue",
        postal_code=listing.postal_code or "?",
        address=listing.address or "inconnue",
        surface=surface,
        nb_pieces=listing.nb_pieces or "inconnues",
        nb_chambres=listing.nb_chambres or "inconnues",
        floor=listing.type_etage or listing.etage or "inconnu",
        components=composants,
        reserve_price=prix,
        price_m2=prix_m2,
        occupancy=occupation,
        auction_date=audience,
        auction_location=lieu_audience,
        visit_date=visite,
        property_details=details,
        source_url=listing.source_url,
        loyer_ref=loyer_ref,
        occupation_discount_hint=scoring["occupation_discount_hint"],
        frais_adjudication_percent=int(float(market["frais_adjudication_ratio"]) * 100),
        strategy_target=scoring["strategy_target"],
        absolute_target=scoring["absolute_target"],
        current_category=categorie_actuelle,
    )

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
    return _city_slug(listing) in set(_market_config()["premium_near_paris"])


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
    bases = _scoring_rules()["location_bases"]
    postal_prefix = (listing.postal_code or "")[:2]
    if _is_paris(listing):
        base = int(bases["paris"])
    elif _is_premium_near_paris(listing):
        base = int(bases["premium_near_paris"])
    elif postal_prefix in {"92", "93", "94"}:
        base = int(bases["idf_core"])
    elif postal_prefix in {"77", "78", "91", "95"}:
        base = int(bases["idf_outer"])
    else:
        base = int(bases["other"])
    return _round_int(base + micro_bonus)


def _score_typologie(listing: AuctionListing) -> int:
    config = _scoring_rules()["typology_scores"]
    typology = _extract_typology(listing)
    if typology in {"STUDIO", "T1", "F1", "T2", "F2"}:
        return int(config["target"])
    if typology in {"T3", "F3"}:
        return int(config["medium"])
    if typology in {"T4", "F4", "T5", "F5"}:
        return int(config["large"])
    if listing.surface_m2 and listing.surface_m2 <= 35:
        return int(config["small_surface_fallback"])
    return int(config["default"])


def _score_surface(surface_m2: float | None) -> int:
    if not surface_m2 or surface_m2 <= 0:
        return int(_scoring_rules()["surface_scores"][0]["score"])
    return _range_score(surface_m2, _scoring_rules()["surface_scores"][1:], 20)


def _weighted_score(items: list[tuple[int, float]]) -> int:
    total_weight = sum(weight for _, weight in items)
    weighted_sum = sum(score * weight for score, weight in items)
    return _round_int(weighted_sum / total_weight) if total_weight else 0


def _estimate_travaux(listing: AuctionListing, llm_estimate: float) -> float:
    reserve_price = listing.reserve_price or 0.0
    details = listing.property_details or {}
    condition_signals = set(details.get("condition_signals") or [])
    rules = _scoring_rules()["travaux_rules"]
    if llm_estimate > 0:
        return round(llm_estimate, 2)
    if "a_renover" in condition_signals:
        return round(max(float(rules["a_renover"]["minimum"]), reserve_price * float(rules["a_renover"]["ratio"])), 2)
    if "a_rafraichir" in condition_signals:
        return round(max(float(rules["a_rafraichir"]["minimum"]), reserve_price * float(rules["a_rafraichir"]["ratio"])), 2)
    if "refait_a_neuf" in condition_signals or "bon_etat" in condition_signals:
        return round(max(0.0, reserve_price * float(rules["bon_etat"]["ratio"])), 2)
    return round(
        max(float(rules["default"]["minimum_if_priced"]) if reserve_price else 0.0, reserve_price * float(rules["default"]["ratio"])),
        2,
    )


def _reference_price_m2(listing: AuctionListing) -> float:
    prefix = (listing.postal_code or "")[:2]
    market = _market_config()
    return float(market["reference_price_m2"].get(prefix, market["reference_price_m2_default"]))


def _market_values(listing: AuctionListing, travaux_estimes: float) -> tuple[float, float, float]:
    reserve_price = listing.reserve_price or 0.0
    surface_m2 = listing.surface_m2 or 0.0
    reference_price_m2 = _reference_price_m2(listing)
    valeur_marche_estimee = round(reference_price_m2 * surface_m2, 2) if surface_m2 else round(reserve_price * 1.15, 2)
    coeff_occupation = _occupancy_discount_coefficient(listing)
    valeur_marche_ajustee = round(valeur_marche_estimee * coeff_occupation, 2)
    cout_total = round(reserve_price * (1 + float(_market_config()["frais_adjudication_ratio"])) + travaux_estimes, 2)
    return valeur_marche_estimee, valeur_marche_ajustee, cout_total


def _score_ratio(ratio: float | None) -> int:
    return _range_score(ratio, _scoring_rules()["price_ratio_scores"], 15) if ratio is not None else 25


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
    else:
        price_m2_score = _range_score(relative_m2, _scoring_rules()["relative_m2_scores"], 22)

    score_prix = _weighted_score([(start_score, 5), (target_score, 15), (price_m2_score, 5)])
    return score_prix, valeur_marche_estimee, valeur_marche_ajustee


def _score_liquidite(listing: AuctionListing, micro_bonus: int) -> int:
    config = _scoring_rules()["liquidity"]
    typology_score = _score_typologie(listing)
    surface_score = _score_surface(listing.surface_m2)
    location_score = _score_localisation(listing, micro_bonus)

    if _is_paris(listing):
        profile = config["tension_transport"]["paris"]
    elif _is_premium_near_paris(listing):
        profile = config["tension_transport"]["premium_near_paris"]
    elif (listing.postal_code or "")[:2] in {"92", "93", "94"}:
        profile = config["tension_transport"]["idf_core"]
    else:
        profile = config["tension_transport"]["other"]

    liquidite_revente = _weighted_score(
        [
            (typology_score, float(config["resale_weights"]["typology"])),
            (surface_score, float(config["resale_weights"]["surface"])),
            (location_score, float(config["resale_weights"]["location"])),
        ]
    )
    return _weighted_score(
        [
            (int(profile["tension"]), float(config["global_weights"]["tension"])),
            (liquidite_revente, float(config["global_weights"]["resale"])),
            (int(profile["transport"]), float(config["global_weights"]["transport"])),
        ]
    )


def _score_occupation(listing: AuctionListing) -> int:
    occupancy = (listing.occupancy_status or "").lower()
    config = _scoring_rules()["occupation_scores"]
    profile = config.get(occupancy, config["default"])
    free_score = int(profile["free_score"])
    risk_score = int(profile["risk_score"])
    return _weighted_score([(free_score, 10), (risk_score, 5)])


def _score_qualite(listing: AuctionListing, quality_bonus: int) -> int:
    details = listing.property_details or {}
    config = _scoring_rules()["quality"]
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
        negative += int(config["renovation_penalty"])
    elif "a_rafraichir" in condition_signals:
        negative += int(config["refresh_penalty"])
    if listing.type_etage == "rez_de_chaussee":
        negative += int(config["rdc_penalty"])

    base = int(config["base"]) + positive * int(config["positive_step"]) - negative * int(config["negative_step"])
    return _round_int(base + quality_bonus)


def _bonus_strategique(listing: AuctionListing) -> int:
    typology = _extract_typology(listing)
    surface_m2 = listing.surface_m2 or 0.0
    for rule in _scoring_rules()["strategic_bonus_rules"]:
        if typology not in set(rule["target_typologies"]):
            continue
        if not float(rule["surface_min"]) <= surface_m2 <= float(rule["surface_max"]):
            continue
        if rule["location"] == "paris" and _is_paris(listing):
            return int(rule["bonus"])
        if rule["location"] == "premium_near_paris" and _is_premium_near_paris(listing):
            return int(rule["bonus"])
    return 0


def _categorie_investissement(score_final: int) -> str:
    thresholds = _scoring_rules()["category_thresholds"]
    if score_final >= int(thresholds["opportunite_rare"]):
        return "opportunite_rare"
    if score_final >= int(thresholds["prioritaire"]):
        return "prioritaire"
    if score_final >= int(thresholds["a_etudier"]):
        return "a_etudier"
    return "hors_cible"


def _recommandation_from_category(category: str) -> str:
    if category in {"opportunite_rare", "prioritaire"}:
        return "fort_potentiel"
    if category == "a_etudier":
        return "a_surveiller"
    return "rejeter"


def _occupancy_discount_coefficient(listing: AuctionListing) -> float:
    config = _market_config()["occupancy_discount_coefficients"]
    return float(config["occupe"]) if (listing.occupancy_status or "").lower() == "occupe" else float(config["default"])


def _prix_max(valeur_marche_estimee: float, listing: AuctionListing, travaux_estimes: float, coefficient: float) -> float:
    valeur_ajustee = valeur_marche_estimee * _occupancy_discount_coefficient(listing)
    return round(max(0.0, valeur_ajustee * coefficient - travaux_estimes) / (1 + float(_market_config()["frais_adjudication_ratio"])), 2)


def _fetch_qualitative_signals(listing: AuctionListing) -> AuctionQualitativeSignals:
    if not settings.OPENAI_API_KEY:
        raise AuctionLLMUnavailableError("OPENAI_API_KEY absente")

    try:
        from openai import OpenAI

        llm = _llm_config()
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=llm["model"],
            messages=[
                {
                    "role": "system",
                    "content": llm["system_prompt"],
                },
                {"role": "user", "content": _build_prompt(listing)},
            ],
            response_format={"type": "json_object"},
            temperature=float(llm["temperature"]),
            timeout=float(llm["timeout"]),
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
    config = _scoring_rules()
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
    score_weights = config["score_weights"]

    score_base = (
        score_cible * float(score_weights["cible"])
        + score_prix * float(score_weights["prix"])
        + score_liquidite * float(score_weights["liquidite"])
        + score_occupation * float(score_weights["occupation"])
        + score_qualite_bien * float(score_weights["qualite"])
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
        prix_max_cible=_prix_max(
            valeur_marche_estimee,
            listing,
            travaux_estimes,
            float(config["prix_max_coefficients"]["cible"]),
        ),
        prix_max_agressif=_prix_max(
            valeur_marche_estimee,
            listing,
            travaux_estimes,
            float(config["prix_max_coefficients"]["agressif"]),
        ),
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
