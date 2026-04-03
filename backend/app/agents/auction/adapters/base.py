"""
base.py - Contrats adapters auctions

Description:
Définit les structures minimales de découverte et de parsing pour une source d'encheres.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Protocol


@dataclass(slots=True)
class RawSession:
    external_id: str
    tribunal: str
    city: str | None
    session_datetime: datetime
    source_url: str
    announced_listing_count: int | None = None


@dataclass(slots=True)
class RawListing:
    external_id: str
    source_url: str
    title: str
    reserve_price: float | None = None
    city: str | None = None
    postal_code: str | None = None
    surface_m2: float | None = None
    occupancy_status: str | None = None
    reference_annonce: str | None = None


@dataclass(slots=True)
class RawListingDetail:
    listing: RawListing
    facts: dict[str, Any] = field(default_factory=dict)


class SourceAdapter(Protocol):
    source_code: str

    def parse_sessions(self, html: str, page_url: str) -> list[RawSession]:
        ...

    def parse_listing_cards(self, html: str, page_url: str, session: RawSession) -> list[RawListing]:
        ...

    def parse_listing_detail(self, html: str, page_url: str, listing: RawListing) -> RawListingDetail:
        ...
