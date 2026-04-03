"""
licitor.py - Adapter source Licitor

Description:
Implémente le parsing minimal Licitor pour audiences et annonces detail.
Le fetch reseau sera branche plus tard sur ce parser testable.
"""

from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.agents.auction.adapters.base import RawListing, RawListingDetail, RawSession


class LicitorAuctionAdapter:
    source_code = "licitor"

    def parse_sessions(self, html: str, page_url: str) -> list[RawSession]:
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text(" ", strip=True)

        tribunal = self._extract_tribunal(page_text, page_url)
        session_datetime = self._extract_session_datetime(page_text)
        announced_listing_count = self._extract_announced_listing_count(page_text)
        external_id = f"{tribunal.lower().replace(' ', '-')}-{session_datetime.strftime('%Y-%m-%d-%H%M')}"
        city = tribunal.replace("TJ ", "").strip() if tribunal.startswith("TJ ") else None

        return [
            RawSession(
                external_id=external_id,
                tribunal=tribunal,
                city=city,
                session_datetime=session_datetime,
                source_url=page_url,
                announced_listing_count=announced_listing_count,
            )
        ]

    def parse_listing_cards(self, html: str, page_url: str, session: RawSession) -> list[RawListing]:
        soup = BeautifulSoup(html, "html.parser")
        listings: list[RawListing] = []
        seen_urls: set[str] = set()

        for link in soup.select('a[href*="/annonce/"]'):
            href = link.get("href")
            if not href:
                continue
            absolute_url = urljoin(page_url, href)
            if absolute_url in seen_urls:
                continue
            seen_urls.add(absolute_url)

            text = " ".join(link.stripped_strings)
            if not text:
                continue

            external_id = self._extract_external_id(absolute_url)
            reserve_price = self._extract_price(text)
            surface_m2 = self._extract_surface(text)
            postal_code = self._extract_postal_code(text)
            city = self._extract_city(text, session.city)

            listings.append(
                RawListing(
                    external_id=external_id,
                    source_url=absolute_url,
                    title=text[:500],
                    reserve_price=reserve_price,
                    city=city,
                    postal_code=postal_code,
                    surface_m2=surface_m2,
                    reference_annonce=external_id,
                )
            )

        return listings

    def discover_paginated_urls(self, html: str, base_url: str) -> list[str]:
        """Retourne toutes les URLs paginées détectées depuis la première page."""
        soup = BeautifulSoup(html, "html.parser")
        page_links = soup.select('a[href*="?p="]')
        page_numbers: set[int] = set()
        for link in page_links:
            href = link.get("href", "")
            match = re.search(r"\?p=(\d+)", href)
            if match:
                page_numbers.add(int(match.group(1)))

        if not page_numbers:
            return []

        base = re.sub(r"\?.*$", "", base_url)
        return [f"{base}?p={n}" for n in sorted(page_numbers)]

    def parse_listing_detail(self, html: str, page_url: str, listing: RawListing) -> RawListingDetail:
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text("\n", strip=True)
        floor_info = self._extract_floor_info(page_text)

        facts = {
            "title": self._first_non_empty(
                self._text_of_first(soup, "h1"),
                listing.title,
            ),
            "reserve_price": self._extract_price(page_text) or listing.reserve_price,
            "surface_m2": self._extract_surface(page_text) or listing.surface_m2,
            "nb_pieces": self._extract_room_count(page_text),
            "nb_chambres": self._extract_bedroom_count(page_text),
            "etage": floor_info["etage"],
            "type_etage": floor_info["type_etage"],
            "ascenseur": self._extract_amenity_presence(page_text, ["ascenseur"], ["sans ascenseur"]),
            "balcon": self._extract_amenity_presence(page_text, ["balcon"], ["sans balcon"]),
            "terrasse": self._extract_amenity_presence(page_text, ["terrasse"], ["sans terrasse"]),
            "cave": self._extract_amenity_presence(page_text, ["cave"], ["sans cave"]),
            "parking": self._extract_amenity_presence(page_text, ["parking", "stationnement"], ["sans parking", "sans stationnement"]),
            "box": self._extract_amenity_presence(page_text, ["box", "garage"], ["sans box", "sans garage"]),
            "jardin": self._extract_amenity_presence(page_text, ["jardin"], ["sans jardin"]),
            "postal_code": self._extract_postal_code(page_text) or listing.postal_code,
            "occupancy_status": self._extract_occupancy_status(page_text),
            "lawyer_phone": self._extract_phone(page_text),
            "documents": self._extract_documents(soup, page_url),
            "visit_dates": self._extract_visit_mentions(page_text),
            "address": self._extract_address(page_text),
            "property_details": self._extract_property_details(page_text),
        }
        return RawListingDetail(listing=listing, facts=facts)

    def _extract_tribunal(self, text: str, page_url: str) -> str:
        slug_match = re.search(r"/(tj-[a-z0-9\-]+)/", page_url)
        if slug_match:
            slug = slug_match.group(1)[3:]
            return "TJ " + slug.replace("-", " ").title()
        tribunal_match = re.search(r"\bTJ\s+[A-Za-zÀ-ÿ]+(?:[\s-]+[A-Za-zÀ-ÿ]+){0,3}", text)
        if tribunal_match:
            tribunal_name = tribunal_match.group(0).replace("-", " ")
            return re.sub(r"\s+", " ", tribunal_name).strip()
        return "TJ INCONNU"

    def _extract_session_datetime(self, text: str) -> datetime:
        months = {
            "janvier": 1, "fevrier": 2, "février": 2, "mars": 3, "avril": 4,
            "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "août": 8,
            "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12, "décembre": 12,
        }
        pattern = re.search(
            r"(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)?\s*(\d{1,2})\s+([A-Za-zÀ-ÿ]+)\s+(\d{4})(?:.*?(\d{1,2})h(?:(\d{2}))?)?",
            text,
            flags=re.IGNORECASE,
        )
        if not pattern:
            return datetime.utcnow()

        day = int(pattern.group(2))
        month_label = pattern.group(3).lower()
        year = int(pattern.group(4))
        hour = int(pattern.group(5) or 0)
        minute = int(pattern.group(6) or 0)
        month = months.get(month_label, 1)
        return datetime(year, month, day, hour, minute)

    def _extract_announced_listing_count(self, text: str) -> int | None:
        match = re.search(r"(\d+)\s+annonces?", text, flags=re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _extract_external_id(self, url: str) -> str:
        match = re.search(r"/annonce/(.+?)\.html", url)
        if match:
            return match.group(1).strip("/")
        return url

    def _extract_price(self, text: str) -> float | None:
        match = re.search(r"mise\s+a\s+prix[^0-9]*(\d[\d\s]*)\s*(?:€|eur)", text, flags=re.IGNORECASE)
        if not match:
            match = re.search(r"(\d[\d\s]{3,})\s*(?:€|eur)", text, flags=re.IGNORECASE)
        if not match:
            return None
        return float(re.sub(r"[^\d]", "", match.group(1)))

    def _extract_surface(self, text: str) -> float | None:
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*m(?:²|2)", text, flags=re.IGNORECASE)
        if not match:
            return None
        return float(match.group(1).replace(",", "."))

    def _extract_room_count(self, text: str) -> int | None:
        match = re.search(r"\b(\d+)\s*pi[eè]ces?\b", text, flags=re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _extract_bedroom_count(self, text: str) -> int | None:
        match = re.search(r"\b(\d+)\s*chambres?\b", text, flags=re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _extract_floor_info(self, text: str) -> dict[str, int | str | None]:
        lowered = text.lower()
        if "rez-de-chauss" in lowered or "rdc" in lowered:
            return {"etage": 0, "type_etage": "rez_de_chaussee"}

        match = re.search(r"\b(\d+)(?:er|e|eme|ème)?\s+etage\b", text, flags=re.IGNORECASE)
        if match:
            type_etage = "dernier_etage" if "dernier etage" in lowered or "dernier étage" in lowered else "etage"
            return {"etage": int(match.group(1)), "type_etage": type_etage}

        if "dernier etage" in lowered or "dernier étage" in lowered:
            return {"etage": None, "type_etage": "dernier_etage"}

        return {"etage": None, "type_etage": None}

    def _extract_postal_code(self, text: str) -> str | None:
        match = re.search(r"\b(75\d{3}|92\d{3}|93\d{3}|94\d{3}|95\d{3}|91\d{3}|77\d{3}|78\d{3})\b", text)
        return match.group(1) if match else None

    def _extract_city(self, text: str, fallback_city: str | None) -> str | None:
        city_match = re.search(r"\bParis(?:\s+\d{1,2}(?:eme|er)?)?\b", text, flags=re.IGNORECASE)
        if city_match:
            return city_match.group(0)
        return fallback_city

    def _extract_occupancy_status(self, text: str) -> str | None:
        lowered = text.lower()
        if "occup" in lowered:
            if "libre" in lowered:
                return "libre"
            return "occupe"
        return None

    def _extract_amenity_presence(
        self,
        text: str,
        positive_keywords: list[str],
        negative_keywords: list[str] | None = None,
    ) -> bool | None:
        lowered = text.lower()
        for negative_keyword in negative_keywords or []:
            if negative_keyword in lowered:
                return False
        for positive_keyword in positive_keywords:
            if positive_keyword in lowered:
                return True
        return None

    def _extract_phone(self, text: str) -> str | None:
        match = re.search(r"\b0[1-9](?:[\s\.-]?\d{2}){4}\b", text)
        return match.group(0) if match else None

    def _extract_documents(self, soup: BeautifulSoup, page_url: str) -> list[str]:
        docs: list[str] = []
        for link in soup.select('a[href$=".pdf"], a[href*=".pdf?"]'):
            href = link.get("href")
            if href:
                docs.append(urljoin(page_url, href))
        return docs

    def _extract_visit_mentions(self, text: str) -> list[str]:
        return re.findall(r"visite[s]?\s*[:\-]?\s*([^\n]+)", text, flags=re.IGNORECASE)

    def _extract_address(self, text: str) -> str | None:
        address_match = re.search(r"\b\d{1,3}[^,\n]+,\s*(75\d{3}\s+[A-Za-zÀ-ÿ\- ]+)", text)
        if address_match:
            return address_match.group(0).strip()
        return None

    def _extract_property_details(self, text: str) -> dict[str, object]:
        typology = self._extract_typology(text)
        floor_info = self._extract_floor_info(text)
        condition_signals = self._extract_keyword_signals(
            text,
            {
                "a_renover": ["a renover", "à rénover", "renovation", "rénovation"],
                "a_rafraichir": ["a rafraichir", "à rafraîchir", "rafraichissement", "rafraîchissement"],
                "bon_etat": ["bon etat", "bon état"],
                "refait_a_neuf": ["refait a neuf", "refait à neuf", "renove", "rénové"],
            },
        )
        layout_signals = self._extract_keyword_signals(
            text,
            {
                "lumineux": ["lumineux", "lumineuse"],
                "traversant": ["traversant", "traversante"],
                "calme": ["calme"],
                "cuisine_ouverte": ["cuisine ouverte"],
                "double_sejour": ["double sejour", "double séjour"],
            },
        )

        amenities = {
            "ascenseur": self._extract_amenity_presence(text, ["ascenseur"], ["sans ascenseur"]),
            "balcon": self._extract_amenity_presence(text, ["balcon"], ["sans balcon"]),
            "terrasse": self._extract_amenity_presence(text, ["terrasse"], ["sans terrasse"]),
            "cave": self._extract_amenity_presence(text, ["cave"], ["sans cave"]),
            "parking": self._extract_amenity_presence(text, ["parking", "stationnement"], ["sans parking", "sans stationnement"]),
            "box": self._extract_amenity_presence(text, ["box", "garage"], ["sans box", "sans garage"]),
            "jardin": self._extract_amenity_presence(text, ["jardin"], ["sans jardin"]),
        }

        details: dict[str, object] = {
            "typology": typology,
            "room_count": self._extract_room_count(text),
            "bedroom_count": self._extract_bedroom_count(text),
            "floor": floor_info,
            "amenities": amenities,
            "condition_signals": condition_signals,
            "layout_signals": layout_signals,
        }
        return {key: value for key, value in details.items() if value not in (None, [], {})}

    def _extract_typology(self, text: str) -> str | None:
        lowered = text.lower()
        for label in ["studio", "t1", "t2", "t3", "t4", "t5", "f1", "f2", "f3", "f4", "f5"]:
            if label in lowered:
                return label.upper()
        if "appartement" in lowered:
            return "APPARTEMENT"
        if "maison" in lowered:
            return "MAISON"
        return None

    def _extract_keyword_signals(self, text: str, mapping: dict[str, list[str]]) -> list[str]:
        lowered = text.lower()
        signals: list[str] = []
        for signal, keywords in mapping.items():
            if any(keyword in lowered for keyword in keywords):
                signals.append(signal)
        return signals

    def _text_of_first(self, soup: BeautifulSoup, selector: str) -> str | None:
        node = soup.select_one(selector)
        return node.get_text(" ", strip=True) if node else None

    def _first_non_empty(self, *values: str | None) -> str:
        for value in values:
            if value:
                return value
        return ""
