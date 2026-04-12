"""
agent.py - Nœud LangGraph ARCHIVIO

Description:
Reçoit un seul pdf_url via Send() (fan-out depuis HERMES).
Télécharge le PDF, extrait les données via LLM, merge dans pdf_extractions.
Non-bloquant : erreur loggée dans state.errors, extraction null.

Dépendances:
- archivio/downloader.py
- archivio/extractor.py

Utilisé par:
- graph/licitor_graph.py (nœud "archivio")
"""

import asyncio
import time
from datetime import datetime, timezone

from app.agents.archivio.downloader import download_pdf
from app.agents.archivio.extractor import run_extraction
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def archivio_node(state: dict) -> dict:
    """Nœud ARCHIVIO — reçoit {pdf_url, listing_url} via Send()."""
    pdf_url: str = state["pdf_url"]
    listing_url: str = state["listing_url"]

    logger.info(f"[ARCHIVIO] Traitement PDF: {pdf_url}")
    t_start = time.time()

    # Téléchargement
    pdf_bytes = asyncio.run(download_pdf(pdf_url))

    if not pdf_bytes:
        return {
            "pdf_extractions": {pdf_url: None},
            "errors": [{
                "node": "archivio",
                "detail": f"PDF download failed: {pdf_url}",
                "ts": datetime.now(timezone.utc).isoformat(),
            }],
        }

    # Extraction LLM
    try:
        result, tokens = run_extraction(pdf_bytes, pdf_url, listing_url)
    except Exception as exc:
        logger.error(f"[ARCHIVIO] Extraction failed {pdf_url}: {exc}")
        return {
            "pdf_extractions": {pdf_url: None},
            "errors": [{
                "node": "archivio",
                "detail": f"LLM extraction failed: {exc}",
                "ts": datetime.now(timezone.utc).isoformat(),
            }],
        }

    duration_ms = int((time.time() - t_start) * 1000)
    logger.info(f"[ARCHIVIO] {pdf_url} extrait en {duration_ms}ms ({tokens} tokens)")

    return {
        "pdf_extractions": {pdf_url: result},
        "token_usage": {"archivio": tokens},
        "durations_ms": {"archivio": duration_ms},
    }
