"""
dvf_client.py - Client API DVF (Demandes de Valeurs Foncières)

Description:
Interroge l'API publique DVF pour obtenir les transactions immobilières
dans un rayon géographique. Cache 24h par (postal_code, type_bien).

Dépendances:
- httpx

Utilisé par:
- mercato/agent.py
"""

import hashlib
import asyncio
from datetime import datetime, timedelta
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

DVF_BASE_URL = "https://api.gouv.fr/les-api/api-dvf"
# API publique réelle : https://api.data.gouv.fr/api/dvf/v1/
DVF_API_URL = "https://api.data.gouv.fr/api/dvf/v1/geomutations/"
DVF_TIMEOUT = 10.0
DVF_RAYON_DEFAULT = 500     # mètres
DVF_RAYON_FALLBACK = 1000   # si < 5 transactions
DVF_PERIODE_MOIS = 24
DVF_MIN_TRANSACTIONS = 5

# Cache en mémoire (clé → {data, expires_at})
_cache: dict[str, dict] = {}


def _cache_key(postal_code: str, type_bien: str) -> str:
    return hashlib.md5(f"{postal_code}:{type_bien}".encode()).hexdigest()


def _get_cache(postal_code: str, type_bien: str) -> dict | None:
    key = _cache_key(postal_code, type_bien)
    entry = _cache.get(key)
    if entry and datetime.utcnow() < entry["expires_at"]:
        return entry["data"]
    return None


def _set_cache(postal_code: str, type_bien: str, data: dict) -> None:
    key = _cache_key(postal_code, type_bien)
    _cache[key] = {
        "data": data,
        "expires_at": datetime.utcnow() + timedelta(hours=24),
    }


async def _fetch_dvf_transactions(postal_code: str, type_bien: str, rayon: int) -> list[dict]:
    """Appelle l'API DVF et retourne les transactions brutes."""
    import httpx

    date_min = (datetime.utcnow() - timedelta(days=DVF_PERIODE_MOIS * 30)).strftime("%Y-%m-%d")

    params = {
        "code_postal": postal_code,
        "type_local": type_bien,
        "date_min": date_min,
        "page_size": 200,
    }

    headers = {"User-Agent": "MezianeMonitoring/1.0"}
    try:
        async with httpx.AsyncClient(headers=headers) as client:
            for attempt in range(1, 3):
                try:
                    resp = await client.get(DVF_API_URL, params=params, timeout=DVF_TIMEOUT)
                    resp.raise_for_status()
                    data = resp.json()
                    return data.get("results", data) if isinstance(data, dict) else data
                except (httpx.HTTPError, httpx.TimeoutException) as exc:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(2)
    except Exception as exc:
        logger.warning(f"DVF API error postal_code={postal_code}: {exc}")
        return []

    return []


def _calculate_prix_m2(transactions: list[dict], surface_m2: float) -> float | None:
    """Calcule le prix médian au m² depuis les transactions DVF."""
    import statistics

    prices_m2 = []
    for t in transactions:
        valeur = t.get("valeur_fonciere") or t.get("prix")
        surface = t.get("surface_reelle_bati") or t.get("surface")
        if valeur and surface and float(surface) > 0:
            # Filtrer surfaces comparables (±30%)
            if abs(float(surface) - surface_m2) / max(surface_m2, 1) <= 0.30:
                prices_m2.append(float(valeur) / float(surface))

    if not prices_m2:
        return None
    return statistics.median(prices_m2)


async def get_price_estimate(listing_url: str, postal_code: str, city: str,
                              surface_m2: float, reserve_price: float,
                              type_bien: str = "Appartement") -> dict:
    """Retourne l'estimation de prix marché pour un listing."""
    if not postal_code or not surface_m2 or not reserve_price:
        return {
            "listing_url": listing_url,
            "source": "unavailable",
            "confidence": "low",
        }

    # Cache
    cached = _get_cache(postal_code, type_bien)
    transactions = cached if cached is not None else []

    if not transactions:
        transactions = await _fetch_dvf_transactions(postal_code, type_bien, DVF_RAYON_DEFAULT)
        if transactions:
            _set_cache(postal_code, type_bien, transactions)

    nb_transactions = len(transactions)
    confidence = "high"
    rayon = DVF_RAYON_DEFAULT

    if nb_transactions < DVF_MIN_TRANSACTIONS:
        # Elargir le rayon
        transactions = await _fetch_dvf_transactions(postal_code, type_bien, DVF_RAYON_FALLBACK)
        nb_transactions = len(transactions)
        confidence = "medium" if nb_transactions >= DVF_MIN_TRANSACTIONS else "low"
        rayon = DVF_RAYON_FALLBACK

    if not transactions:
        logger.info(f"[MERCATO] 0 transactions DVF pour {postal_code}")
        return {
            "listing_url": listing_url,
            "source": "unavailable",
            "confidence": "low",
            "nb_transactions": 0,
        }

    prix_m2_marche = _calculate_prix_m2(transactions, surface_m2)
    if not prix_m2_marche:
        return {
            "listing_url": listing_url,
            "source": "dvf",
            "confidence": "low",
            "nb_transactions": nb_transactions,
        }

    prix_m2_mise_a_prix = reserve_price / surface_m2 if surface_m2 else None
    ratio = reserve_price / (surface_m2 * prix_m2_marche) if surface_m2 and prix_m2_marche else None

    return {
        "listing_url": listing_url,
        "prix_m2_marche": round(prix_m2_marche, 2),
        "prix_m2_mise_a_prix": round(prix_m2_mise_a_prix, 2) if prix_m2_mise_a_prix else None,
        "ratio": round(ratio, 4) if ratio else None,
        "nb_transactions": nb_transactions,
        "rayon_metres": rayon,
        "periode_mois": DVF_PERIODE_MOIS,
        "source": "dvf",
        "confidence": confidence,
    }
