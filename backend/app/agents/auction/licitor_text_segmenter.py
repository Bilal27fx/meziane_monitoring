"""
licitor_text_segmenter.py - Découpe le texte brut d'une page Licitor en sections nommées

Description:
Identifie les frontières entre sections d'une page annonce Licitor (header, enchère,
lots, adresse, visite, avocat) sans extraire de valeurs. Les sections sont renvoyées
brutes au LLM pour extraction structurée.

Dependances:
- aucune (stdlib seulement)

Utilise par:
- licitor_llm_extraction_service.py
- adapters/licitor.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class LicitorPageSections:
    header: str = ""
    auction_block: str = ""
    lots: list[str] = field(default_factory=list)
    address_block: str = ""
    visit_block: str = ""
    lawyer_block: str = ""
    raw_text: str = ""


_LOT_MARKER = re.compile(
    r"^\s*(?:\d+(?:er|ème|eme|nd|e)?)\s+lot\s+de\s+la\s+vente",
    flags=re.IGNORECASE,
)
_AUCTION_KEYWORDS = re.compile(
    r"vente\s+aux\s+ench[eè]res|vente\s+judiciaire|adjudication",
    flags=re.IGNORECASE,
)
_DATE_LINE = re.compile(
    r"\b(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b.*\d{4}",
    flags=re.IGNORECASE,
)
_TIME_LINE = re.compile(r"\b\d{1,2}h\d{0,2}\b", flags=re.IGNORECASE)
_POSTAL_CODE = re.compile(r"\b\d{5}\b")
_VISIT_KEYWORDS = re.compile(r"\bvisite\b|\bsur\s+place\b", flags=re.IGNORECASE)
_LAWYER_KEYWORDS = re.compile(
    r"\bme\.?\s+[A-ZÀ-ÿ]|\bma[iî]tre\s+[A-ZÀ-ÿ]|\bavocat\b",
    flags=re.IGNORECASE,
)
_TRIBUNAL_KEYWORDS = re.compile(
    r"\btribunal\b|\bannexe\b|\btj\s+",
    flags=re.IGNORECASE,
)


def segment_licitor_page(raw_text: str) -> LicitorPageSections:
    """Découpe le texte brut d'une page annonce Licitor en sections nommées."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    sections = LicitorPageSections(raw_text=raw_text)

    if not lines:
        return sections

    # Trouver les indices de frontière
    first_lot_idx = _find_first_lot_index(lines)
    visit_idx = _find_visit_index(lines)
    lawyer_idx = _find_lawyer_index(lines)

    # --- Header : avant le premier marqueur de lot ou d'enchère ---
    auction_start = _find_auction_block_start(lines, first_lot_idx)
    header_end = auction_start if auction_start > 0 else (first_lot_idx if first_lot_idx > 0 else len(lines))
    sections.header = "\n".join(lines[:header_end])

    # --- Auction block : mentions de la vente + date/heure ---
    auction_end = first_lot_idx if first_lot_idx > 0 else _find_lots_end(lines, 0, visit_idx)
    sections.auction_block = "\n".join(lines[auction_start:auction_end]) if auction_start < auction_end else sections.header

    # --- Lots : du premier marqueur de lot jusqu'à l'adresse ---
    if first_lot_idx >= 0:
        lots_end = _find_lots_end(lines, first_lot_idx, visit_idx)
        lot_chunk = lines[first_lot_idx:lots_end]
        sections.lots = _split_lots(lot_chunk)
        address_start = lots_end
    else:
        address_start = auction_end

    # --- Address block : après les lots, avant la visite ---
    address_end = visit_idx if visit_idx >= 0 else (lawyer_idx if lawyer_idx >= 0 else len(lines))
    if address_end > address_start:
        address_lines = [
            l for l in lines[address_start:address_end]
            if not _VISIT_KEYWORDS.search(l) and not _LAWYER_KEYWORDS.search(l)
        ]
        sections.address_block = "\n".join(address_lines)

    # --- Visit block ---
    if visit_idx >= 0:
        visit_end = lawyer_idx if lawyer_idx > visit_idx else len(lines)
        sections.visit_block = "\n".join(lines[visit_idx:visit_end])

    # --- Lawyer block ---
    if lawyer_idx >= 0:
        sections.lawyer_block = "\n".join(lines[lawyer_idx:])

    return sections


def _find_first_lot_index(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if _LOT_MARKER.match(line):
            return i
    return -1


def _find_auction_block_start(lines: list[str], first_lot_idx: int) -> int:
    """Trouve la première ligne qui parle de la vente (avant les lots)."""
    limit = first_lot_idx if first_lot_idx > 0 else len(lines)
    for i, line in enumerate(lines[:limit]):
        if _AUCTION_KEYWORDS.search(line) or _DATE_LINE.search(line):
            return i
    return 0


def _find_lots_end(lines: list[str], start: int, visit_idx: int) -> int:
    """Trouve la fin du bloc lots — début de l'adresse."""
    limit = visit_idx if visit_idx > start else len(lines)
    # On remonte depuis la limite pour trouver la dernière ligne qui semble faire partie d'un lot
    for i in range(limit - 1, start - 1, -1):
        line = lines[i]
        if _LOT_MARKER.match(line):
            continue
        # Une ligne de mise à prix est la fin d'un lot
        if re.search(r"mise\s+[aà]\s+prix", line, flags=re.IGNORECASE):
            return i + 1
    return limit


def _split_lots(lot_lines: list[str]) -> list[str]:
    """Sépare les lignes en chunks individuels par lot."""
    lots: list[str] = []
    current: list[str] = []

    for line in lot_lines:
        if _LOT_MARKER.match(line) and current:
            lots.append("\n".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        lots.append("\n".join(current))

    return lots if lots else ["\n".join(lot_lines)]


def _find_visit_index(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if _VISIT_KEYWORDS.search(line):
            return i
    return -1


def _find_lawyer_index(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if _LAWYER_KEYWORDS.search(line):
            return i
    return -1
