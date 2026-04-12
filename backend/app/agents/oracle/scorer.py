"""
scorer.py - Scoring déterministe Python — sans LLM

Description:
Calcule le score numérique (0-100) et la décision BUY/WATCH/SKIP.
Le LLM n'est utilisé que pour la justification textuelle (dans agent.py).

Dépendances:
- aucune (logique pure Python)

Utilisé par:
- oracle/agent.py
"""

from datetime import datetime

# ── Seuils de décision ─────────────────────────────────────────────────────
DECISION_THRESHOLDS = {
    "BUY": 70,
    "WATCH": 45,
}

# ── Poids par dimension ────────────────────────────────────────────────────
WEIGHTS = {
    "ratio_prix": 35,
    "surface_type": 15,
    "etat_bien": 10,
    "occupation": 10,
    "localisation": 10,
    "visite_possible": 10,
    "donnees_pdf": 10,
}


def score_ratio_prix(price_est: dict | None) -> int:
    """Score basé sur le ratio mise_a_prix / prix_marché (max 35)."""
    if not price_est or price_est.get("source") == "unavailable":
        return 15  # score neutre si pas de données marché
    ratio = price_est.get("ratio")
    if ratio is None:
        return 15
    if ratio < 0.40:
        return 35
    if ratio < 0.50:
        return 30
    if ratio < 0.65:
        return 22
    if ratio < 0.80:
        return 14
    if ratio < 1.00:
        return 7
    return 0  # sur-évalué


def score_surface_type(listing: dict) -> int:
    """Score surface et type de bien (max 15)."""
    surface = listing.get("surface_m2") or 0
    if surface <= 0:
        return 0
    if surface >= 60:
        return 15
    if surface >= 40:
        return 12
    if surface >= 25:
        return 8
    if surface >= 15:
        return 4
    return 0  # < 15m² → deal breaker géré ailleurs


def score_etat_bien(pdf_ext: dict | None) -> int:
    """Score état général depuis extraction PDF (max 10)."""
    if not pdf_ext:
        return 5  # neutre si pas de PDF
    etat = (pdf_ext.get("etat_general") or "").lower()
    if etat == "bon":
        return 10
    if etat == "moyen":
        return 6
    if etat == "dégradé":
        return 2
    return 5  # null → neutre


def score_occupation(listing: dict) -> int:
    """Score statut occupation (max 10)."""
    status = (listing.get("occupancy_status") or "").lower()
    if "libre" in status:
        return 10
    if "occupé" in status or "occupe" in status:
        return 2
    return 6  # inconnu → neutre


def score_localisation(listing: dict) -> int:
    """Score localisation (max 10). IDF + grandes villes favorisées."""
    postal_code = listing.get("postal_code") or ""
    city = (listing.get("city") or "").upper()

    # IDF (75, 92, 93, 94)
    if postal_code.startswith(("75", "92", "93", "94")):
        return 10
    # Grandes villes
    grandes_villes = ["LYON", "MARSEILLE", "BORDEAUX", "NANTES", "TOULOUSE",
                      "NICE", "STRASBOURG", "MONTPELLIER", "RENNES", "LILLE"]
    if any(v in city for v in grandes_villes):
        return 8
    # Autre ville connue
    if postal_code:
        return 5
    return 2


def score_visite_possible(listing: dict) -> int:
    """Score visite disponible avant enchère (max 10)."""
    visit_dates = listing.get("visit_dates") or []
    if not visit_dates:
        return 0
    # Vérifier si au moins une visite est dans le futur
    now = datetime.utcnow()
    for d in visit_dates:
        try:
            dt = datetime.fromisoformat(d) if isinstance(d, str) else d
            if dt > now:
                return 10
        except (ValueError, TypeError):
            continue
    return 5  # visites passées → données présentes mais non applicables


def score_donnees_pdf(pdf_ext: dict | None) -> int:
    """Score richesse des données PDF (max 10)."""
    if not pdf_ext:
        return 0
    fields = ["surface_m2", "charges_annuelles", "dpe_classe", "etat_general", "syndic"]
    filled = sum(1 for f in fields if pdf_ext.get(f) is not None)
    return min(filled * 2, 10)


def check_deal_breakers(listing: dict, price_est: dict | None) -> list[str]:
    """Retourne la liste des deal breakers qui forcent SKIP."""
    breakers = []
    surface = listing.get("surface_m2") or 0
    if surface > 0 and surface < 15:
        breakers.append("surface<15m2")

    occupancy = (listing.get("occupancy_status") or "").lower()
    ratio = (price_est or {}).get("ratio")
    if ("occupé" in occupancy or "occupe" in occupancy) and (ratio is None or ratio > 0.60):
        breakers.append("occupé+ratio>0.60")

    if not listing.get("auction_date"):
        breakers.append("date_enchere_inconnue")

    return breakers


def detect_flags(listing: dict, price_est: dict | None, score: int) -> list[str]:
    """Détecte les flags informatifs."""
    flags = []
    now = datetime.utcnow()

    # Visite imminente
    for d in (listing.get("visit_dates") or []):
        try:
            dt = datetime.fromisoformat(d) if isinstance(d, str) else d
            delta = (dt - now).days
            if 0 <= delta <= 7:
                flags.append("visite_imminente")
                break
        except (ValueError, TypeError):
            continue

    # Enchère imminente
    auction_date_str = listing.get("auction_date")
    if auction_date_str:
        try:
            dt = datetime.fromisoformat(auction_date_str)
            if 0 <= (dt - now).days <= 14:
                flags.append("enchère_imminente")
        except (ValueError, TypeError):
            pass

    # Ratio exceptionnel
    ratio = (price_est or {}).get("ratio")
    if ratio and ratio < 0.50:
        flags.append("ratio_exceptionnel")

    # Données incomplètes
    if not (price_est and price_est.get("source") != "unavailable"):
        flags.append("données_incomplètes")

    return flags


def compute_score(listing: dict, pdf_ext: dict | None, price_est: dict | None) -> dict:
    """Calcule le score complet d'un listing. Retourne le dict résultat ORACLE."""
    # Deal breakers en premier
    deal_breakers = check_deal_breakers(listing, price_est)
    if deal_breakers:
        return {
            "listing_url": listing.get("source_url", ""),
            "score": 0,
            "decision": "SKIP",
            "breakdown": {k: 0 for k in WEIGHTS},
            "deal_breakers": deal_breakers,
            "flags": [],
            "justification": None,  # rempli par le LLM dans agent.py
        }

    # Calcul par dimension
    breakdown = {
        "ratio_prix": score_ratio_prix(price_est),
        "surface_type": score_surface_type(listing),
        "etat_bien": score_etat_bien(pdf_ext),
        "occupation": score_occupation(listing),
        "localisation": score_localisation(listing),
        "visite_possible": score_visite_possible(listing),
        "donnees_pdf": score_donnees_pdf(pdf_ext),
    }

    total = sum(breakdown.values())
    total = min(total, 100)

    # Décision
    if total >= DECISION_THRESHOLDS["BUY"]:
        decision = "BUY"
    elif total >= DECISION_THRESHOLDS["WATCH"]:
        decision = "WATCH"
    else:
        decision = "SKIP"

    flags = detect_flags(listing, price_est, total)

    return {
        "listing_url": listing.get("source_url", ""),
        "score": total,
        "decision": decision,
        "breakdown": breakdown,
        "deal_breakers": [],
        "flags": flags,
        "justification": None,  # rempli par le LLM dans agent.py
    }
