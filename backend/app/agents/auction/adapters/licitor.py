"""
licitor.py - Adapter source Licitor

Description:
Implémente le parsing minimal Licitor pour audiences et annonces detail.
Le fetch reseau sera branche plus tard sur ce parser testable.
"""

from __future__ import annotations

import re
from datetime import datetime
from html import unescape
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.agents.auction.adapters.base import RawListing, RawListingDetail, RawSession


class LicitorAuctionAdapter:
    source_code = "licitor"

    def parse_sessions(self, html: str, page_url: str) -> list[RawSession]:
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text(" ", strip=True)

        tribunal = self._extract_tribunal(page_text, page_url)
        session_datetime = self._extract_session_datetime(page_text, page_url)
        announced_listing_count = self._extract_announced_listing_count(page_text)
        if session_datetime is not None:
            external_id = f"{tribunal.lower().replace(' ', '-')}-{session_datetime.strftime('%Y-%m-%d-%H%M')}"
        else:
            external_id = f"{tribunal.lower().replace(' ', '-')}-{page_url.rstrip('/').split('/')[-1]}"
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
        extracted_address = self._extract_address(page_text)
        visit_details = self._extract_visit_details(page_text, extracted_address)

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
            "visit_dates": visit_details["dates"],
            "address": extracted_address,
            "property_details": self._extract_property_details(page_text, visit_details),
        }
        return RawListingDetail(listing=listing, facts=facts)

    def _extract_tribunal(self, text: str, page_url: str) -> str:
        slug_match = re.search(r"/(tj-[a-z0-9\-]+)/", page_url)
        if slug_match:
            slug = slug_match.group(1)[3:]
            return "TJ " + slug.replace("-", " ").title()
        tribunal_judiciaire_match = re.search(
            r"(?:\bA\s+l['’]annexe\s+du\s+)?\bTribunal\s+Judiciaire\s+de\s+"
            r"([A-Za-zÀ-ÿ]+(?:[\s-]+[A-Za-zÀ-ÿ]+){0,3}?)"
            r"(?:\s+\([^)]+\))?"
            r"(?=\s+(?:Vente|Audience|lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b|$)",
            text,
            flags=re.IGNORECASE,
        )
        if tribunal_judiciaire_match:
            city = re.sub(r"\s+", " ", tribunal_judiciaire_match.group(1).replace("-", " ")).strip()
            return f"TJ {city.title()}"
        tribunal_match = re.search(r"\bTJ\s+[A-Za-zÀ-ÿ]+(?:[\s-]+[A-Za-zÀ-ÿ]+){0,3}", text)
        if tribunal_match:
            tribunal_name = tribunal_match.group(0).replace("-", " ")
            return re.sub(r"\s+", " ", tribunal_name).strip()
        return "TJ INCONNU"

    def _extract_session_datetime(self, text: str, page_url: str | None = None) -> datetime | None:
        months = {
            "janvier": 1, "fevrier": 2, "février": 2, "mars": 3, "avril": 4,
            "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "août": 8,
            "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12, "décembre": 12,
        }
        lines = self._clean_lines(text)

        for candidate in self._candidate_session_blocks(text, lines, page_url):
            date_match = re.search(
                r"(?:(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+)?"
                r"(\d{1,2})\s+([A-Za-zÀ-ÿ]+)\s+(\d{4})",
                candidate,
                flags=re.IGNORECASE,
            )
            if not date_match:
                date_match = re.search(
                    r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b",
                    candidate,
                    flags=re.IGNORECASE,
                )

            if not date_match:
                continue

            if "/" in date_match.group(0):
                day = int(date_match.group(1))
                month = int(date_match.group(2))
                year = int(date_match.group(3))
                if year < 100:
                    year += 2000
            else:
                day = int(date_match.group(1))
                month_label = date_match.group(2).lower()
                year = int(date_match.group(3))
                month = months.get(month_label)
                if month is None:
                    continue

            time_match = re.search(
                r"\b(?:audience\s*[aà]?\s*|vente\s*[aà]?\s*)?(\d{1,2})h(?:(\d{2}))?\b",
                candidate,
                flags=re.IGNORECASE,
            )
            if not time_match:
                time_match = re.search(
                    r"\b(?:audience\s*[aà]?\s*|vente\s*[aà]?\s*)?(\d{1,2})h(?:(\d{2}))?\b",
                    text,
                    flags=re.IGNORECASE,
                )
            hour = int(time_match.group(1)) if time_match else 0
            minute = int(time_match.group(2) or 0) if time_match else 0
            return datetime(year, month, day, hour, minute)

        return None  # date non trouvée — session créée sans datetime

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
        if any(token in lowered for token in ["rez-de-chauss", "rez de chauss", "rez-de-jardin", "rez de jardin", "rdc"]):
            return {"etage": 0, "type_etage": "rez_de_chaussee"}

        floor_patterns = [
            r"\bau\s+(\d+)(?:er|e|eme|ème)?\s+etage\b",
            r"\bsitue?\s+au\s+(\d+)(?:er|e|eme|ème)?\s+etage\b",
            r"\b(\d+)(?:er|e|eme|ème)?\s+etage\b",
            r"\betage\s+(\d+)\b",
            r"\b(\d+)(?:er|e|eme|ème)?\s*/\s*\d+(?:er|e|eme|ème)?\s+etage\b",
        ]
        for pattern in floor_patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                type_etage = "dernier_etage" if "dernier etage" in lowered or "dernier étage" in lowered else "etage"
                return {"etage": int(match.group(1)), "type_etage": type_etage}

        if "dernier etage" in lowered or "dernier étage" in lowered:
            return {"etage": None, "type_etage": "dernier_etage"}

        return {"etage": None, "type_etage": None}

    def _extract_postal_code(self, text: str) -> str | None:
        for match in re.finditer(r"\b(\d{5})\b", text):
            cp = match.group(1)
            if 1000 <= int(cp) <= 97680:  # plage CP France métropolitaine + DOM
                return cp
        return None

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

    def _extract_visit_details(self, text: str, fallback_address: str | None) -> dict[str, object]:
        lines = self._clean_lines(text)
        candidate_blocks = self._extract_visit_blocks(lines)

        month_labels = "janvier|fevrier|février|mars|avril|mai|juin|juillet|aout|août|septembre|octobre|novembre|decembre|décembre"
        date_pattern = re.compile(
            r"(?:(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+)?"
            rf"\d{{1,2}}(?:er)?\s+(?:{month_labels})(?:\s+\d{{4}})?"
            r"(?:\s+de\s+\d{1,2}h(?:\d{2})?\s+[aà]\s+\d{1,2}h(?:\d{2})?)?",
            flags=re.IGNORECASE,
        )
        numeric_date_pattern = re.compile(
            r"\b\d{1,2}/\d{1,2}/\d{2,4}(?:\s+de\s+\d{1,2}h(?:\d{2})?\s+[aà]\s+\d{1,2}h(?:\d{2})?)?",
            flags=re.IGNORECASE,
        )
        explicit_location_pattern = re.compile(
            r"\b(?:au|a l'adresse|à l'adresse|adresse|sur place au|sur place a|rendez-vous au|rdv au)\s+"
            r"(\d{1,4}[^\n]{5,120})",
            flags=re.IGNORECASE,
        )

        visit_dates: list[str] = []
        for block_lines in candidate_blocks:
            block = " ".join(block_lines)
            for match in date_pattern.findall(block) + numeric_date_pattern.findall(block):
                cleaned = re.sub(r"\s+", " ", match).strip(" ,;:-")
                if cleaned and cleaned not in visit_dates:
                    visit_dates.append(cleaned)

        visit_location = None
        for block_lines in candidate_blocks:
            block = " ".join(block_lines)
            location_match = explicit_location_pattern.search(block)
            if location_match:
                visit_location = location_match.group(1).strip(" ,;:-")
                break

        return {
            "dates": visit_dates,
            "location": visit_location,
        }

    def _extract_address(self, text: str) -> str | None:
        lines = self._clean_lines(text)
        filtered_lines = [
            line
            for line in lines
            if not self._is_non_property_line(line)
        ]
        postal_fragment = r"(?:[0-9]{5})\s+[A-Za-zÀ-ÿ’’\- ]+"

        prefixed_patterns = [
            rf"\b(?:adresse|situ[ée]?\s+a|sis|situé au|située au)\s*[:\-]?\s*(\d{{1,4}}[^,\n]*?,\s*{postal_fragment})",
            rf"\b(?:adresse|situ[ée]?\s+a|sis|situé au|située au)\s*[:\-]?\s*(\d{{1,4}}[^\n]*?\s+{postal_fragment})",
        ]
        for line in filtered_lines:
            for pattern in prefixed_patterns:
                match = re.search(pattern, line, flags=re.IGNORECASE)
                if match:
                    return re.sub(r"\s+", " ", match.group(1)).strip(" ,;:-")

        generic_patterns = [
            rf"\b(\d{{1,4}}[^,\n]*?,\s*{postal_fragment})",
            rf"\b(\d{{1,4}}[^\n]*?\s+{postal_fragment})",
        ]
        for line in filtered_lines:
            for pattern in generic_patterns:
                match = re.search(pattern, line, flags=re.IGNORECASE)
                if match:
                    return re.sub(r"\s+", " ", match.group(1)).strip(" ,;:-")
        return None

    def _extract_property_details(self, text: str, visit_details: dict[str, object] | None = None) -> dict[str, object]:
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
            "visit": visit_details or None,
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

    def _clean_lines(self, text: str) -> list[str]:
        return [
            re.sub(r"\s+", " ", unescape(line)).strip(" ,;:-\t")
            for line in text.splitlines()
            if line.strip()
        ]

    def _candidate_session_blocks(self, text: str, lines: list[str], page_url: str | None) -> list[str]:
        candidates: list[str] = []

        if lines:
            header_block = " ".join(lines[: min(4, len(lines))])
            candidates.append(header_block)

        for index, line in enumerate(lines):
            lowered = line.lower()
            if any(
                keyword in lowered
                for keyword in [
                    "audience",
                    "ventes judiciaires",
                    "vente judiciaire",
                    "adjudication",
                    "tribunal judiciaire",
                    "vente aux encheres",
                    "vente aux enchères",
                ]
            ):
                block_lines = [line]
                for offset in range(1, 4):
                    if index + offset < len(lines):
                        block_lines.append(lines[index + offset])
                candidates.append(" ".join(block_lines))

        candidates.append(text)

        if page_url:
            slug = page_url.rstrip("/").split("/")[-1]
            slug = slug.removesuffix(".html").replace("-", " ")
            candidates.append(slug)
            candidates.append(f"{slug} {text}")

        deduped: list[str] = []
        for candidate in candidates:
            normalized = re.sub(r"\s+", " ", candidate).strip()
            if normalized and normalized not in deduped:
                deduped.append(normalized)
        return deduped

    def _extract_visit_blocks(self, lines: list[str]) -> list[list[str]]:
        blocks: list[list[str]] = []
        stop_keywords = (
            "mise a prix",
            "mise à prix",
            "surface",
            "cahier",
            "occupation",
            "bien occupe",
            "bien occupé",
            "avocat",
            "descriptif",
        )
        # Pattern pour les références d'avocat (Me. Nom ou Me Nom) — évite de couper sur "même", "mise", etc.
        avocat_pattern = re.compile(r"\bMe\.?\s+[A-Z][a-z]", re.IGNORECASE)
        phone_pattern = re.compile(r"\b0[1-9](?:[\s\.\-]?\d{2}){4}\b")

        for index, line in enumerate(lines):
            lowered = line.lower()
            if "visite" not in lowered and "sur place" not in lowered:
                continue

            block_lines = [line]
            for offset in range(1, 7):
                next_index = index + offset
                if next_index >= len(lines):
                    break
                next_line = lines[next_index]
                if any(keyword in next_line.lower() for keyword in stop_keywords):
                    break
                if avocat_pattern.search(next_line) or phone_pattern.search(next_line):
                    break
                block_lines.append(next_line)
                if len(next_line) > 180:
                    break

            blocks.append(block_lines)

        return blocks

    def _is_non_property_line(self, line: str) -> bool:
        lowered = line.lower()
        return any(
            keyword in lowered
            for keyword in [
                "visite",
                "rendez-vous",
                "rdv",
                "audience",
                "adjudication",
                "enchere",
                "enchère",
                "avocat",
            ]
        ) or bool(re.search(r"\bMe\.\s+[A-Z]", line)) or bool(re.search(r"\b0[1-9](?:[\s\.-]?\d{2}){4}\b", line))
