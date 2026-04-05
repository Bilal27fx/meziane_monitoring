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
import re
from typing import Any, Optional

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.auction_listing import AuctionListing

logger = logging.getLogger(__name__)

_SCORING_CONFIG_PATH = Path(__file__).with_name("auction_scoring_config.json")
_PROMPT_VARIABLE_PATTERN = re.compile(r"{([a-zA-Z_][a-zA-Z0-9_]*)}")


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
    valeur_prudente: float
    prix_interessant: float
    prix_palier: float
    raison_score: str
    risques: list[str]
    recommandation: str
    penalty_usage: int = 0
    penalty_uncertainty: int = 0
    penalty_surface: int = 0
    penalty_deal_breaker: int = 0
    deal_breaker_triggered: bool = False


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


def _range_score(value: float | None, rules: list[dict[str, Any]] | dict[str, Any], default_score: int) -> int:
    if value is None:
        return default_score
    normalized_rules = rules.get("brackets", []) if isinstance(rules, dict) else rules
    for rule in normalized_rules:
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
    estimated_auction_price = _estimated_auction_price(listing)
    estimated_market_value = _estimated_market_value(listing)
    conservative_market_value = _conservative_market_value(
        listing,
        estimated_market_value,
        travaux_documented=bool((listing.property_details or {}).get("condition_signals")),
    )
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
    values = {
        "title": listing.title,
        "listing_type": listing.listing_type or "inconnu",
        "city": listing.city or "inconnue",
        "postal_code": listing.postal_code or "?",
        "address": listing.address or "inconnue",
        "surface": surface,
        "nb_pieces": listing.nb_pieces or "inconnues",
        "nb_chambres": listing.nb_chambres or "inconnues",
        "floor": listing.type_etage or listing.etage or "inconnu",
        "components": composants,
        "reserve_price": prix,
        "price_m2": prix_m2,
        "occupancy": occupation,
        "estimated_auction_price": f"{estimated_auction_price:,.0f}€" if estimated_auction_price else "inconnu",
        "auction_price_multiplier": _auction_price_multiplier(),
        "market_value_estimated": f"{estimated_market_value:,.0f}€" if estimated_market_value else "inconnu",
        "conservative_market_value": f"{conservative_market_value:,.0f}€" if conservative_market_value else "inconnu",
        "usage_type": _usage_type(listing),
        "auction_date": audience,
        "auction_location": lieu_audience,
        "visit_date": visite,
        "property_details": details,
        "source_url": listing.source_url,
        "loyer_ref": loyer_ref,
        "occupation_discount_hint": scoring["occupation_discount_hint"],
        "frais_adjudication_percent": int(float(market["frais_adjudication_ratio"]) * 100),
        "strategy_target": scoring["strategy_target"],
        "absolute_target": scoring["absolute_target"],
        "current_category": categorie_actuelle,
    }

    def replace_placeholder(match: re.Match[str]) -> str:
        key = match.group(1)
        return str(values.get(key, match.group(0)))

    return _PROMPT_VARIABLE_PATTERN.sub(replace_placeholder, llm["user_prompt_template"])

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


def _location_cluster(listing: AuctionListing) -> str:
    if _is_paris(listing):
        return "paris"

    hierarchy = _scoring_rules().get("location_hierarchy", {})
    city = _city_slug(listing)
    for cluster_name in ("premiere_couronne_liquide", "premiere_couronne_solide"):
        if city in set(hierarchy.get(cluster_name, [])):
            return cluster_name

    postal_prefix = (listing.postal_code or "")[:2]
    if postal_prefix in {"92", "93", "94"}:
        return "idf_core"
    if postal_prefix in {"77", "78", "91", "95"}:
        return "idf_outer"
    return "other"


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
    cluster = _location_cluster(listing)
    base = int(bases[cluster])
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


def _auction_price_multiplier() -> float:
    pricing = _scoring_rules()["auction_adjusted_price"]
    if bool(pricing.get("use_avg_for_scoring", True)):
        return float(pricing["multiplier"]["avg"])
    return float(pricing["multiplier"]["min"])


def _estimated_auction_price(listing: AuctionListing) -> float:
    reserve_price = listing.reserve_price or 0.0
    return round(reserve_price * _auction_price_multiplier(), 2) if reserve_price > 0 else 0.0


def _estimated_market_value(listing: AuctionListing) -> float:
    reserve_price = listing.reserve_price or 0.0
    surface_m2 = listing.surface_m2 or 0.0
    reference_price_m2 = _reference_price_m2(listing)
    if surface_m2 > 0:
        return round(reference_price_m2 * surface_m2, 2)
    return round(reserve_price * 1.15, 2)


def _usage_type(listing: AuctionListing) -> str:
    details = listing.property_details or {}
    raw_candidates = [
        details.get("usage"),
        listing.listing_type,
        listing.title,
    ]
    normalized = " ".join(str(value or "").lower() for value in raw_candidates)
    if any(token in normalized for token in {"bureau", "bureaux"}):
        return "bureau"
    if any(token in normalized for token in {"commerce", "commercial", "local commercial", "boutique"}):
        return "commerce"
    return "habitation"


def _risk_flags(listing: AuctionListing, travaux_documented: bool) -> set[str]:
    details = listing.property_details or {}
    flags: set[str] = set()
    condition_signals = set(details.get("condition_signals") or [])
    if not condition_signals:
        flags.add("etat_inconnu")
    if not travaux_documented:
        flags.add("travaux_non_documentes")
    if listing.ascenseur is None and (listing.etage or 0) >= 3:
        flags.add("ascenseur_inconnu_etage_eleve")
    if _usage_type(listing) != "habitation":
        flags.add("bien_atypique")
    elif _extract_typology(listing) in {"T4", "F4", "T5", "F5", "APPARTEMENT"} and (listing.surface_m2 or 0) > 55:
        flags.add("bien_atypique")
    return flags


def _conservative_market_value(listing: AuctionListing, market_value: float, travaux_documented: bool) -> float:
    adjusted = round(market_value * _occupancy_discount_coefficient(listing), 2)
    risk_config = _scoring_rules()["risk_adjustment"]
    if _risk_flags(listing, travaux_documented) & set(risk_config["apply_if"]):
        return round(adjusted * float(risk_config["valeur_prudente_coeff"]), 2)
    return adjusted


def _reference_price_m2(listing: AuctionListing) -> float:
    prefix = (listing.postal_code or "")[:2]
    market = _market_config()
    return float(market["reference_price_m2"].get(prefix, market["reference_price_m2_default"]))


def _market_values(listing: AuctionListing, travaux_estimes: float) -> tuple[float, float, float]:
    valeur_marche_estimee = _estimated_market_value(listing)
    prix_estime_enchere = _estimated_auction_price(listing)
    valeur_marche_ajustee = round(valeur_marche_estimee * _occupancy_discount_coefficient(listing), 2)
    valeur_prudente = _conservative_market_value(listing, valeur_marche_estimee, travaux_documented=travaux_estimes > 0)
    cout_total = round(prix_estime_enchere * (1 + float(_market_config()["frais_adjudication_ratio"])) + travaux_estimes, 2)
    return valeur_marche_estimee, valeur_marche_ajustee, valeur_prudente, cout_total


def _score_prix(listing: AuctionListing) -> int:  # Compare la mise a prix reelle/m2 au marche du secteur
    reserve_price = listing.reserve_price or 0.0
    surface_m2 = listing.surface_m2 or 0.0
    reference_price_m2 = _reference_price_m2(listing)
    if not reserve_price or not surface_m2 or not reference_price_m2:
        return 25
    ratio = (reserve_price / surface_m2) / reference_price_m2
    return _range_score(ratio, _scoring_rules()["price_ratio_scores"], 15)


def _score_composition(listing: AuctionListing, quality_bonus: int) -> int:  # Typologie + etat + annexes
    config = _scoring_rules()["composition_scoring"]
    details = listing.property_details or {}
    typology = _extract_typology(listing)
    score = int(config["base"])

    if typology in {"STUDIO", "T1", "F1", "T2", "F2"} and _usage_type(listing) == "habitation":
        score += int(config["target_typology_bonus"])

    if listing.balcon or listing.terrasse or listing.jardin:
        score += int(config["annexe_bonus"])
    if listing.cave or listing.parking or listing.box:
        score += int(config["storage_bonus"])
    if listing.etage is not None and listing.etage >= 1:
        score += int(config["floor_bonus"])
    if listing.ascenseur and (listing.etage or 0) >= 3:
        score += int(config["ascenseur_bonus"])
    if "lumineux" in set(details.get("layout_signals") or []):
        score += int(config["lumineux_bonus"])

    condition_signals = set(details.get("condition_signals") or [])
    if "refait_a_neuf" in condition_signals:
        score += int(config["refait_bonus"])
    elif "bon_etat" in condition_signals:
        score += int(config["bon_etat_bonus"])
    elif "a_rafraichir" in condition_signals:
        score -= int(config["rafraichir_penalty"])
    elif "a_renover" in condition_signals:
        score -= int(config["renover_penalty"])

    if listing.type_etage == "rez_de_chaussee":
        score -= int(config["rdc_penalty"])

    return _round_int(score + quality_bonus)


def _score_liquidite(listing: AuctionListing, micro_bonus: int) -> int:
    config = _scoring_rules()["liquidity"]
    typology_score = _score_typologie(listing)
    surface_score = _score_surface(listing.surface_m2)
    location_score = _score_localisation(listing, micro_bonus)
    profile = config["tension_transport"][_location_cluster(listing)]

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


def _uncertainty_penalty(listing: AuctionListing) -> int:
    config = _scoring_rules()["uncertainty_penalty"]
    details = listing.property_details or {}
    missing = 0
    for field in config["missing_fields"]:
        if field == "etat" and not details.get("condition_signals"):
            missing += 1
        elif field == "ascenseur" and listing.ascenseur is None and (listing.etage or 0) >= 3:
            missing += 1
        elif field == "distribution" and (listing.surface_m2 or 0) >= 25 and not details.get("layout_signals"):
            missing += 1
        elif (
            field == "charges"
            and _usage_type(listing) == "habitation"
            and (listing.listing_type or "").lower() == "appartement"
            and details.get("charges") in {"inconnu"}
        ):
            missing += 1
    penalty = missing * int(config["penalty_per_missing"])
    return max(int(config["max_penalty"]), penalty)


def _surface_penalty(listing: AuctionListing) -> int:
    rules = _scoring_rules()["surface_rules"]
    surface = listing.surface_m2 or 0.0
    if 0 < surface < 12:
        return int(rules["<12"])
    if 12 <= surface < 14:
        return int(rules["12-14"])
    if 14 <= surface < 18:
        return int(rules["14-18"])
    return 0


def _deal_breaker_penalty(
    listing: AuctionListing,
    conservative_market_value: float,
    travaux_estimes: float,
) -> tuple[int, bool]:
    config = _scoring_rules()["deal_breakers"]
    if not config.get("enabled", False):
        return 0, False

    occupancy = (listing.occupancy_status or "").strip().lower()
    reserve_price = listing.reserve_price or 0.0
    penalty = 0
    triggered = False
    for rule in config["rules"]:
        condition = rule["condition"]
        if condition == "surface < 12" and (listing.surface_m2 or 0) > 0 and (listing.surface_m2 or 0) < 12:
            penalty += int(rule["penalty"])
            if rule.get("triggers_cap", True):
                triggered = True
        elif condition == "cout_minimum > valeur_prudente" and reserve_price > 0 and conservative_market_value > 0:
            cout_minimum = reserve_price * (1 + float(_market_config()["frais_adjudication_ratio"])) + travaux_estimes
            if cout_minimum > conservative_market_value * 1.05:
                penalty += int(rule["penalty"])
                if rule.get("triggers_cap", True):
                    triggered = True
        elif condition == "occupation == inconnu" and occupancy in {"", "inconnu", "a_verifier"}:
            penalty += int(rule["penalty"])
            if rule.get("triggers_cap", True):
                triggered = True
    return penalty, triggered


def _usage_penalty(listing: AuctionListing) -> int:
    penalties = _scoring_rules()["usage_penalty"]
    usage = _usage_type(listing)
    return int(penalties.get(usage, 0))


def _effective_micro_bonus(listing: AuctionListing, micro_bonus: int) -> int:
    adjustment = _scoring_rules()["location_adjustment"]
    if micro_bonus <= 0:
        return micro_bonus
    liquidity_confirmed = _score_typologie(listing) >= 60 and _score_surface(listing.surface_m2) >= 60
    if adjustment.get("require_liquidity_confirmation", False) and not liquidity_confirmed:
        return min(micro_bonus, int(adjustment["max_bonus_if_risk"]))
    if _risk_flags(listing, travaux_documented=False):
        return min(micro_bonus, int(adjustment["max_bonus_if_risk"]))
    return micro_bonus


def _bonus_strategique(listing: AuctionListing) -> int:
    if _usage_type(listing) != "habitation":
        return 0
    typology = _extract_typology(listing)
    surface_m2 = listing.surface_m2 or 0.0
    cluster = _location_cluster(listing)
    for rule in _scoring_rules()["strategic_bonus_rules"]:
        if typology not in set(rule["target_typologies"]):
            continue
        if not float(rule["surface_min"]) <= surface_m2 <= float(rule["surface_max"]):
            continue
        if rule["location"] == "paris" and _is_paris(listing):
            return int(rule["bonus"])
        if rule["location"] == cluster:
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


def _log_scoring_breakdown(
    listing: AuctionListing,
    result: AuctionScoringBreakdown,
    *,
    cluster: str,
    estimated_auction_price: float,
    usage_penalty: int,
    uncertainty_penalty: int,
    surface_penalty: int,
    deal_breaker_penalty: int,
    deal_breaker_triggered: bool,
) -> None:
    logger.info(
        (
            "Scoring breakdown listing %s | ville=%s | cluster=%s | score=%s | categorie=%s | "
            "cible=%s prix=%s liquidite=%s occupation=%s qualite=%s bonus=%s | "
            "penalites: usage=%s incertitude=%s surface=%s deal_breaker=%s triggered=%s | "
            "prix_estime=%s valeur_marche=%s valeur_prudente=%s prix_interessant=%s prix_palier=%s | "
            "travaux=%s loyer=%s renta=%s"
        ),
        listing.id,
        listing.city or "?",
        cluster,
        result.score_global,
        result.categorie_investissement,
        result.score_cible_paris_petite_surface,
        result.score_prix,
        result.score_liquidite,
        result.score_occupation,
        result.score_qualite_bien,
        result.bonus_strategique,
        usage_penalty,
        uncertainty_penalty,
        surface_penalty,
        deal_breaker_penalty,
        deal_breaker_triggered,
        round(estimated_auction_price, 2),
        round(result.valeur_marche_estimee, 2),
        round(result.valeur_marche_ajustee, 2),
        round(result.prix_interessant, 2),
        round(result.prix_palier, 2),
        round(result.travaux_estimes, 2),
        round(result.loyer_estime, 2),
        round(result.rentabilite_brute, 2),
    )


def _occupancy_discount_coefficient(listing: AuctionListing) -> float:
    config = _market_config()["occupancy_discount_coefficients"]
    occupancy = (listing.occupancy_status or "").lower()
    if occupancy == "occupe":
        return float(config["occupe"])
    if occupancy in {"", "inconnu", "a_verifier"}:
        return float(config.get("inconnu", config["default"]))
    return float(config["default"])


def _prix_max(valeur_marche_estimee: float, listing: AuctionListing, travaux_estimes: float, coefficient: float) -> float:  # Calcule le prix max d'enchere pour un coefficient donne
    valeur_prudente = _conservative_market_value(listing, valeur_marche_estimee, travaux_documented=travaux_estimes > 0)
    return round(max(0.0, valeur_prudente * coefficient - travaux_estimes) / (1 + float(_market_config()["frais_adjudication_ratio"])), 2)


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
    effective_micro_bonus = _effective_micro_bonus(listing, qualitative.micro_localisation_bonus)

    # 5 dimensions independantes
    score_localisation = _score_localisation(listing, effective_micro_bonus)
    score_surface = _score_surface(listing.surface_m2)
    score_prix = _score_prix(listing)
    score_composition = _score_composition(listing, qualitative.qualite_bien_bonus)
    score_occupation = _score_occupation(listing)

    # Score cible maintenu pour affichage (blend localisation + typology + surface)
    score_cible = _weighted_score(
        [
            (score_localisation, 15),
            (_score_typologie(listing), 10),
            (score_surface, 10),
        ]
    )

    bonus_strategique = _bonus_strategique(listing)
    usage_penalty = _usage_penalty(listing)
    uncertainty_penalty = _uncertainty_penalty(listing)
    surface_penalty = _surface_penalty(listing)

    valeur_marche_estimee, valeur_marche_ajustee, valeur_prudente, _ = _market_values(listing, travaux_estimes)

    deal_breaker_penalty, deal_breaker_triggered = _deal_breaker_penalty(
        listing,
        conservative_market_value=valeur_prudente,
        travaux_estimes=travaux_estimes,
    )

    score_weights = config["score_weights"]
    score_base = (
        score_localisation * float(score_weights["localisation"])
        + score_surface * float(score_weights["surface"])
        + score_prix * float(score_weights["prix"])
        + score_composition * float(score_weights["composition"])
        + score_occupation * float(score_weights["occupation"])
    )
    adjusted_score = score_base + bonus_strategique + usage_penalty + uncertainty_penalty + surface_penalty + deal_breaker_penalty
    score_global = _round_int(min(100.0, adjusted_score))
    if deal_breaker_triggered:
        score_global = min(score_global, int(config["deal_breakers"]["score_cap"]))

    categorie = _categorie_investissement(score_global)
    estimated_auction_price = _estimated_auction_price(listing)
    rentabilite_brute = round(((loyer_estime * 12) / estimated_auction_price) * 100, 2) if estimated_auction_price > 0 and loyer_estime > 0 else 0.0

    return AuctionScoringBreakdown(
        score_global=score_global,
        score_localisation=score_localisation,
        score_prix=score_prix,
        score_potentiel=score_composition,
        score_cible_paris_petite_surface=score_cible,
        score_liquidite=score_composition,
        score_occupation=score_occupation,
        score_qualite_bien=score_composition,
        bonus_strategique=bonus_strategique,
        categorie_investissement=categorie,
        loyer_estime=loyer_estime,
        rentabilite_brute=rentabilite_brute,
        travaux_estimes=travaux_estimes,
        valeur_marche_estimee=valeur_marche_estimee,
        valeur_marche_ajustee=valeur_marche_ajustee,
        valeur_prudente=valeur_prudente,
        prix_interessant=_prix_max(
            valeur_marche_estimee,
            listing,
            travaux_estimes,
            float(config["prix_max_coefficients"]["interessant"]["coeff"]),
        ),
        prix_palier=_prix_max(
            valeur_marche_estimee,
            listing,
            travaux_estimes,
            float(config["prix_max_coefficients"]["palier"]["coeff"]),
        ),
        raison_score=qualitative.raison_score,
        risques=qualitative.risques,
        recommandation=_recommandation_from_category(categorie),
        penalty_usage=usage_penalty,
        penalty_uncertainty=uncertainty_penalty,
        penalty_surface=surface_penalty,
        penalty_deal_breaker=deal_breaker_penalty,
        deal_breaker_triggered=deal_breaker_triggered,
    )


def score_listing(listing: AuctionListing, db: Session) -> bool:
    try:
        qualitative = _fetch_qualitative_signals(listing)
    except AuctionLLMUnavailableError as exc:
        logger.error("Listing %s non scoré — LLM indisponible: %s", listing.id, exc)
        return False

    result = _compute_scoring(listing, qualitative)
    cluster = _location_cluster(listing)
    estimated_auction_price = _estimated_auction_price(listing)

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
    listing.prix_max_cible = result.prix_interessant
    listing.prix_max_agressif = result.prix_palier
    listing.raison_score = result.raison_score
    listing.risques_llm = result.risques
    listing.recommandation = result.recommandation
    listing.scored_at = datetime.utcnow()

    db.flush()
    logger.info("Listing %s scoré : %s/100 (%s)", listing.id, result.score_global, result.categorie_investissement)
    _log_scoring_breakdown(
        listing,
        result,
        cluster=cluster,
        estimated_auction_price=estimated_auction_price,
        usage_penalty=result.penalty_usage,
        uncertainty_penalty=result.penalty_uncertainty,
        surface_penalty=result.penalty_surface,
        deal_breaker_penalty=result.penalty_deal_breaker,
        deal_breaker_triggered=result.deal_breaker_triggered,
    )
    return True
