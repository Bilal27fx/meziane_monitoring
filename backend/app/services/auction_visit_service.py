"""
auction_visit_service.py - Parsing et fenetrage des visites auctions

Description:
Centralise le parsing des dates de visite en texte libre et la selection
de la prochaine visite actionnable pour l'affichage et les notifications.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import re
from zoneinfo import ZoneInfo

from app.models.auction_listing import AuctionListing

_PARIS_TZ = ZoneInfo("Europe/Paris")
_DEFAULT_VISIT_HOUR = 9
_MONTHS = {
    "janvier": 1,
    "fevrier": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "aout": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "decembre": 12,
}
_TEXT_NORMALIZER = str.maketrans(
    {
        "à": "a",
        "â": "a",
        "ä": "a",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ö": "o",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
    }
)
_ISO_DATE_PATTERN = re.compile(r"(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?")
_NUMERIC_DATE_PATTERN = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b")
_TEXTUAL_DATE_PATTERN = re.compile(
    r"\b(\d{1,2})(?:er)?\s+"
    r"(janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)"
    r"(?:\s+(\d{4}))?\b",
    flags=re.IGNORECASE,
)
_TIME_PATTERN = re.compile(r"\b(\d{1,2})h(?:(\d{2}))?\b", flags=re.IGNORECASE)


def paris_now() -> datetime:
    return datetime.now(_PARIS_TZ).replace(tzinfo=None)


def _normalize_visit_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower().translate(_TEXT_NORMALIZER))


def _extract_time_components(raw_value: str) -> tuple[int, int]:
    match = _TIME_PATTERN.search(_normalize_visit_text(raw_value))
    if not match:
        return _DEFAULT_VISIT_HOUR, 0
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    return hour, minute


def parse_visit_datetime(raw_value: str, fallback_year: int | None = None) -> datetime | None:
    if not raw_value:
        return None

    # Format ISO : 2026-04-24T12:00:00 ou 2026-04-24
    iso_match = _ISO_DATE_PATTERN.match(raw_value.strip())
    if iso_match:
        try:
            year = int(iso_match.group(1))
            month = int(iso_match.group(2))
            day = int(iso_match.group(3))
            hour = int(iso_match.group(4) or _DEFAULT_VISIT_HOUR)
            minute = int(iso_match.group(5) or 0)
            return datetime(year, month, day, hour, minute)
        except ValueError:
            pass

    normalized = _normalize_visit_text(raw_value)
    hour, minute = _extract_time_components(raw_value)

    numeric_match = _NUMERIC_DATE_PATTERN.search(normalized)
    if numeric_match:
        day = int(numeric_match.group(1))
        month = int(numeric_match.group(2))
        year = int(numeric_match.group(3))
        if year < 100:
            year += 2000
        try:
            return datetime(year, month, day, hour, minute)
        except ValueError:
            return None

    textual_match = _TEXTUAL_DATE_PATTERN.search(normalized)
    if textual_match:
        day = int(textual_match.group(1))
        month = _MONTHS[textual_match.group(2).lower()]
        year = int(textual_match.group(3) or fallback_year or paris_now().year)
        try:
            return datetime(year, month, day, hour, minute)
        except ValueError:
            return None

    return None


def get_next_visit_schedule(
    listing: AuctionListing,
    reference: datetime | None = None,
) -> tuple[str, datetime] | None:
    reference = reference or paris_now()
    fallback_year = listing.auction_date.year if listing.auction_date else reference.year
    candidates: list[tuple[str, datetime]] = []

    for raw_visit in listing.visit_dates or []:
        if not isinstance(raw_visit, str):
            continue
        parsed = parse_visit_datetime(raw_visit, fallback_year=fallback_year)
        if parsed is None or parsed < reference:
            continue
        candidates.append((raw_visit, parsed))

    if not candidates:
        return None

    return min(candidates, key=lambda item: item[1])


def get_actionable_visit_datetime(
    listing: AuctionListing,
    window_days: int = 10,
    reference: datetime | None = None,
) -> datetime | None:
    if listing.categorie_investissement not in {"prioritaire", "opportunite_rare", "a_etudier"}:
        return None

    reference = reference or paris_now()
    visit_schedule = get_next_visit_schedule(listing, reference=reference)
    if visit_schedule is None:
        return None

    _, visit_datetime = visit_schedule
    if visit_datetime > reference + timedelta(days=window_days):
        return None
    return visit_datetime
