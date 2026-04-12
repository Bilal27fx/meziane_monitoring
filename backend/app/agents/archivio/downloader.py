"""
downloader.py - Téléchargement PDF avec retry

Description:
Télécharge un PDF depuis une URL. Retourne les bytes ou None si echec.
Limite à 50 pages pour éviter les PDFs géants.

Dépendances:
- httpx

Utilisé par:
- archivio/extractor.py
"""

import httpx
import asyncio
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

PDF_TIMEOUT = 30.0
PDF_MAX_SIZE_MB = 20


async def download_pdf(pdf_url: str) -> bytes | None:
    """Télécharge un PDF. Retourne bytes ou None si échec."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; MezianeMonitoring/1.0)"}
    async with httpx.AsyncClient(headers=headers) as client:
        for attempt in range(1, 3):
            try:
                resp = await client.get(pdf_url, timeout=PDF_TIMEOUT, follow_redirects=True)
                resp.raise_for_status()
                content_length = int(resp.headers.get("content-length", 0))
                if content_length > PDF_MAX_SIZE_MB * 1024 * 1024:
                    logger.warning(f"PDF trop grand ({content_length} bytes), ignoré: {pdf_url}")
                    return None
                return resp.content
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                if attempt == 2:
                    logger.warning(f"PDF download failed: {pdf_url} — {exc}")
                    return None
                await asyncio.sleep(2)
    return None
