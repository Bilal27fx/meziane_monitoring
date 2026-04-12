"""
parser.py - Parsing des pages de détail Licitor → raw_listings

Description:
Transforme le HTML brut des pages de détail en dicts structurés.
Utilise l'adapter pour le parsing HTML + normalisation des champs.

Dépendances:
- beautifulsoup4
- hermes/fetcher.py (SourceAdapter, ADAPTERS)

Utilisé par:
- hermes/agent.py
"""

import re
from datetime import datetime
from app.utils.logger import setup_logger
from app.agents.hermes.fetcher import ADAPTERS

logger = setup_logger(__name__)

_DATE_FORMATS = [
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y",
    "%d-%m-%Y %H:%M",
    "%d-%m-%Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
]


def _parse_date(text: str) -> str | None:
    """Tente de parser une date depuis un texte libre."""
    if not text:
        return None
    # Nettoyage
    text = text.strip()
    # Chercher un pattern date dans le texte
    m = re.search(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})", text)
    if m:
        day, month, year = m.group(1), m.group(2), m.group(3)
        # Chercher heure
        hm = re.search(r"(\d{1,2})[h:](\d{2})", text)
        if hm:
            try:
                dt = datetime(int(year), int(month), int(day), int(hm.group(1)), int(hm.group(2)))
                return dt.isoformat()
            except ValueError:
                pass
        try:
            dt = datetime(int(year), int(month), int(day))
            return dt.isoformat()
        except ValueError:
            pass
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text[:len(fmt)], fmt).isoformat()
        except ValueError:
            continue
    return None


def _extract_reserve_price(text: str) -> float | None:
    """Extrait un prix numérique depuis un texte (ex: '120 000 €' → 120000.0)."""
    if not text:
        return None
    clean = text.replace("\xa0", "").replace(" ", "").replace("€", "").replace(".", "").replace(",", ".")
    m = re.search(r"[\d]+(?:\.\d+)?", clean)
    if m:
        try:
            return float(m.group())
        except ValueError:
            pass
    return None


def build_raw_listings(session_result: dict, source_code: str) -> list[dict]:
    """Construit la liste raw_listings depuis le résultat fetch_session."""
    adapter = ADAPTERS.get(source_code)
    if not adapter:
        return []

    listings = []
    listing_pages: dict[str, str] = session_result.get("listing_pages", {})
    pdf_urls: dict[str, list[str]] = session_result.get("pdf_urls", {})

    for listing_url, html in listing_pages.items():
        try:
            raw = adapter.parse_listing_detail(html, listing_url)
        except Exception as exc:
            logger.warning(f"Erreur parse_listing_detail {listing_url}: {exc}")
            raw = {"source_url": listing_url, "external_id": listing_url.rstrip("/").split("/")[-1]}

        # Normaliser reserve_price si c'est encore une string
        if isinstance(raw.get("reserve_price"), str):
            raw["reserve_price"] = _extract_reserve_price(raw["reserve_price"])

        # Normaliser auction_date
        if isinstance(raw.get("auction_date"), str) and raw["auction_date"]:
            parsed_date = _parse_date(raw["auction_date"])
            if parsed_date:
                raw["auction_date"] = parsed_date

        # Enrichir avec pdf_urls connus
        raw["pdf_urls"] = pdf_urls.get(listing_url, [])

        # Assurer les champs obligatoires
        raw.setdefault("external_id", listing_url.rstrip("/").split("/")[-1])
        raw.setdefault("source_url", listing_url)

        listings.append(raw)

    return listings
