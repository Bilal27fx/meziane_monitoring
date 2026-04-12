"""
agent.py - Nœud LangGraph HERMES

Description:
Collecte les pages Licitor pour toutes les session_urls.
Produit raw_pages[], raw_listings[] dans le state.
Bloquant si 0 listing trouvé.

Dépendances:
- hermes/fetcher.py
- hermes/parser.py

Utilisé par:
- graph/licitor_graph.py (nœud "hermes")
"""

import asyncio
import time
from datetime import datetime, timezone

from app.agents.hermes.fetcher import fetch_session
from app.agents.hermes.parser import build_raw_listings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def hermes_node(state: dict) -> dict:
    """Nœud HERMES — fetch + parse toutes les sessions."""
    run_id = state["run_id"]
    source_code = state["source_code"]
    session_urls = state["session_urls"]

    logger.info(f"[HERMES] run_id={run_id} — {len(session_urls)} session(s) à fetcher")
    t_start = time.time()

    raw_pages = []
    raw_listings = []
    errors = []

    async def _fetch_all():
        tasks = [fetch_session(url, source_code) for url in session_urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

    results = asyncio.run(_fetch_all())

    for url, result in zip(session_urls, results):
        if isinstance(result, Exception):
            logger.error(f"[HERMES] Erreur session {url}: {result}")
            errors.append({
                "node": "hermes",
                "detail": f"fetch_session failed for {url}: {result}",
                "ts": datetime.now(timezone.utc).isoformat(),
            })
            continue

        # Ajouter les erreurs non-bloquantes remontées par le fetcher
        errors.extend(result.get("errors", []))

        raw_pages.append({
            "url": url,
            "session_html": result["session_html"],
            "listing_pages": result["listing_pages"],
            "pdf_urls": result["pdf_urls"],
            "raw_session": result.get("raw_session", {}),
        })

        listings = build_raw_listings(result, source_code)
        raw_listings.extend(listings)

    if not raw_listings:
        raise RuntimeError(
            f"[HERMES] run_id={run_id} — 0 listing trouvé sur {len(session_urls)} session(s). Run arrêté."
        )

    duration_ms = int((time.time() - t_start) * 1000)
    logger.info(f"[HERMES] run_id={run_id} — {len(raw_listings)} listings collectés en {duration_ms}ms")

    return {
        "raw_pages": raw_pages,
        "raw_listings": raw_listings,
        "errors": errors,
        "durations_ms": {"hermes": duration_ms},
    }
