"""
agent.py - Nœud LangGraph MERCATO

Description:
Enrichit chaque listing avec une estimation du prix marché DVF.
Tourne en parallèle avec ARCHIVIO après HERMES.
Non-bloquant : erreur DVF → price_estimates[listing_url] = {source: "unavailable"}.

Dépendances:
- mercato/dvf_client.py

Utilisé par:
- graph/licitor_graph.py (nœud "mercato")
"""

import asyncio
import time
from datetime import datetime, timezone

from app.agents.mercato.dvf_client import get_price_estimate
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def mercato_node(state: dict) -> dict:
    """Nœud MERCATO — enrichit tous les listings avec le prix marché DVF."""
    raw_listings = state.get("raw_listings", [])
    logger.info(f"[MERCATO] {len(raw_listings)} listings à enrichir")
    t_start = time.time()
    errors = []

    async def _enrich_all():
        tasks = []
        for listing in raw_listings:
            tasks.append(get_price_estimate(
                listing_url=listing.get("source_url", ""),
                postal_code=listing.get("postal_code", ""),
                city=listing.get("city", ""),
                surface_m2=listing.get("surface_m2") or 0,
                reserve_price=listing.get("reserve_price") or 0,
                type_bien=_guess_type_bien(listing),
            ))
        return await asyncio.gather(*tasks, return_exceptions=True)

    results = asyncio.run(_enrich_all())
    price_estimates: dict = {}

    for listing, result in zip(raw_listings, results):
        listing_url = listing.get("source_url", "")
        if isinstance(result, Exception):
            logger.warning(f"[MERCATO] Erreur DVF pour {listing_url}: {result}")
            errors.append({
                "node": "mercato",
                "detail": f"DVF error for {listing_url}: {result}",
                "ts": datetime.now(timezone.utc).isoformat(),
            })
            price_estimates[listing_url] = {"source": "unavailable", "confidence": "low"}
        else:
            if result.get("source") == "unavailable":
                errors.append({
                    "node": "mercato",
                    "detail": f"DVF unavailable for postal_code={listing.get('postal_code')}",
                    "ts": datetime.now(timezone.utc).isoformat(),
                })
            price_estimates[listing_url] = result

    duration_ms = int((time.time() - t_start) * 1000)
    logger.info(f"[MERCATO] {len(price_estimates)} estimations en {duration_ms}ms")

    return {
        "price_estimates": price_estimates,
        "errors": errors,
        "durations_ms": {"mercato": duration_ms},
    }


def _guess_type_bien(listing: dict) -> str:
    """Détermine le type de bien pour la requête DVF."""
    type_bien = (listing.get("type_bien") or listing.get("title") or "").upper()
    if "MAISON" in type_bien:
        return "Maison"
    return "Appartement"  # défaut
