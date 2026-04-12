"""
fetcher.py - HTTP fetch Licitor avec adapter pattern

Description:
Fetch des pages Licitor avec retry, rate limiting et timeout.
Délègue le parsing à un SourceAdapter selon source_code.

Dépendances:
- httpx
- beautifulsoup4

Utilisé par:
- hermes/agent.py
"""

import time
import asyncio
from typing import Protocol, runtime_checkable
from dataclasses import dataclass, field
import httpx
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

FETCH_TIMEOUT = 15.0      # secondes par requête
FETCH_RETRY = 3           # tentatives max
RATE_LIMIT_DELAY = 1.0    # pause entre requêtes (secondes)

# URL canonique Licitor — enchères IDF actives
LICITOR_IDF_URL = (
    "https://www.licitor.com/ventes-aux-encheres-immobilieres/"
    "paris-et-ile-de-france/prochaines-ventes.html"
)

# URLs par région (extensible)
LICITOR_URLS: dict[str, str] = {
    "idf": LICITOR_IDF_URL,
}


@dataclass
class RawCard:
    listing_url: str
    external_id: str = ""
    title: str = ""


@dataclass
class RawSession:
    tribunal: str = ""
    city: str = ""
    session_datetime: str = ""
    external_id: str = ""


@runtime_checkable
class SourceAdapter(Protocol):
    def parse_session(self, html: str, url: str) -> RawSession: ...
    def parse_listing_cards(self, html: str, url: str) -> list[RawCard]: ...
    def parse_listing_detail(self, html: str, url: str) -> dict: ...
    def discover_pdf_urls(self, html: str, url: str) -> list[str]: ...
    def discover_pagination(self, html: str, base_url: str) -> list[str]: ...


class LicitorAdapter:
    """Adapter pour licitor.fr — parsing BeautifulSoup des pages d'audience."""

    def parse_session(self, html: str, url: str) -> RawSession:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        session = RawSession()
        try:
            # Titre page contient généralement "Audience - TJ Paris - 15/05/2026"
            title_tag = soup.find("h1") or soup.find("h2")
            if title_tag:
                text = title_tag.get_text(" ", strip=True)
                # Extraire tribunal
                if " - " in text:
                    parts = text.split(" - ")
                    if len(parts) >= 2:
                        session.tribunal = parts[1].strip()
                    if len(parts) >= 3:
                        session.city = parts[1].strip()
            # external_id depuis URL
            session.external_id = url.rstrip("/").split("/")[-1]
        except Exception as exc:
            logger.warning(f"parse_session partiel: {exc}")
        return session

    def parse_listing_cards(self, html: str, url: str) -> list[RawCard]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        cards = []
        # Licitor liste les biens dans des éléments .bien-item ou article
        for el in soup.select("article.bien-item, div.bien-item, .lot-item, .annonce-item"):
            link = el.find("a", href=True)
            if not link:
                continue
            href = link["href"]
            if not href.startswith("http"):
                from urllib.parse import urljoin
                href = urljoin(url, href)
            title_el = el.find(class_=lambda c: c and "title" in c.lower()) or el.find("h2") or el.find("h3")
            title = title_el.get_text(strip=True) if title_el else ""
            # external_id depuis URL
            ext_id = href.rstrip("/").split("/")[-1]
            cards.append(RawCard(listing_url=href, external_id=ext_id, title=title))
        return cards

    def parse_listing_detail(self, html: str, url: str) -> dict:
        from bs4 import BeautifulSoup
        import re
        from datetime import datetime
        soup = BeautifulSoup(html, "html.parser")
        data: dict = {
            "source_url": url,
            "external_id": url.rstrip("/").split("/")[-1],
        }

        def _text(selector: str) -> str:
            el = soup.select_one(selector)
            return el.get_text(strip=True) if el else ""

        def _find_label(label_text: str) -> str:
            """Trouve la valeur associée à un label dans la page."""
            for el in soup.find_all(string=re.compile(label_text, re.I)):
                parent = el.parent
                sibling = parent.find_next_sibling()
                if sibling:
                    return sibling.get_text(strip=True)
                # Essayer le parent suivant
                next_p = parent.find_next(["td", "dd", "span", "div"])
                if next_p:
                    return next_p.get_text(strip=True)
            return ""

        # Titre
        h1 = soup.find("h1")
        data["title"] = h1.get_text(strip=True) if h1 else ""

        # Prix de réserve / mise à prix
        price_text = _find_label(r"mise à prix|prix de réserve|enchère minimum")
        if price_text:
            nums = re.findall(r"[\d\s]+", price_text.replace("\xa0", "").replace(" ", ""))
            if nums:
                try:
                    data["reserve_price"] = float("".join(nums[0].split()))
                except ValueError:
                    pass

        # Surface
        surface_text = _find_label(r"surface|superficie")
        if surface_text:
            m = re.search(r"([\d,\.]+)\s*m²?", surface_text)
            if m:
                try:
                    data["surface_m2"] = float(m.group(1).replace(",", "."))
                except ValueError:
                    pass

        # Ville / code postal
        addr_text = _find_label(r"adresse|localisation|commune")
        if addr_text:
            data["address"] = addr_text
            cp_m = re.search(r"\b(\d{5})\b", addr_text)
            if cp_m:
                data["postal_code"] = cp_m.group(1)
                data["city"] = addr_text.replace(cp_m.group(1), "").strip().strip(",").strip()

        # Tribunal
        data["tribunal"] = _find_label(r"tribunal|juridiction")

        # Date enchère
        date_text = _find_label(r"date.*enchère|audience|jugement")
        if date_text:
            data["auction_date"] = date_text  # parsing poussé dans parser.py

        # Occupation
        occup = _find_label(r"occupation|statut|libre|occupé")
        if occup:
            low = occup.lower()
            if "libre" in low:
                data["occupancy_status"] = "libre"
            elif "occupé" in low or "occupe" in low:
                data["occupancy_status"] = "occupé"

        # Nombre de pièces
        pieces_text = _find_label(r"pièces|nb.*pièces|nombre.*pièces")
        if pieces_text:
            m = re.search(r"(\d+)", pieces_text)
            if m:
                data["nb_pieces"] = int(m.group(1))

        # Avocat
        data["lawyer_name"] = _find_label(r"avocat|mandataire")
        data["lawyer_phone"] = _find_label(r"téléphone|tél\.|tel\.")

        return data

    def discover_pdf_urls(self, html: str, url: str) -> list[str]:
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin
        soup = BeautifulSoup(html, "html.parser")
        pdfs = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf") or "pdf" in href.lower():
                if not href.startswith("http"):
                    href = urljoin(url, href)
                pdfs.append(href)
        return list(set(pdfs))

    def discover_pagination(self, html: str, base_url: str) -> list[str]:
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
        import re
        soup = BeautifulSoup(html, "html.parser")
        pages = []

        # Chercher liens de pagination
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if re.search(r"[?&]p=\d+", href) or re.search(r"[?&]page=\d+", href):
                full = urljoin(base_url, href) if not href.startswith("http") else href
                if full != base_url and full not in pages:
                    pages.append(full)

        # Si pas de pagination trouvée, chercher pattern numérique
        if not pages:
            last_page_el = soup.select_one(".pagination .last, .pager-last, [class*='last']")
            if last_page_el:
                href = last_page_el.get("href", "")
                m = re.search(r"[?&]p=(\d+)", href)
                if m:
                    last = int(m.group(1))
                    parsed = urlparse(base_url)
                    for i in range(2, last + 1):
                        qs = parse_qs(parsed.query)
                        qs["p"] = [str(i)]
                        new_url = urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))
                        pages.append(new_url)

        return pages


ADAPTERS: dict[str, SourceAdapter] = {
    "licitor": LicitorAdapter(),
    # "certeurop": CerteuropAdapter(),  ← ajouter une source ici
}


async def _fetch_with_retry(client: httpx.AsyncClient, url: str) -> str | None:
    """Fetch HTTP avec retry exponentiel. Retourne HTML ou None si echec."""
    for attempt in range(1, FETCH_RETRY + 1):
        try:
            resp = await client.get(url, timeout=FETCH_TIMEOUT, follow_redirects=True)
            resp.raise_for_status()
            return resp.text
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            if attempt == FETCH_RETRY:
                logger.warning(f"Fetch failed après {FETCH_RETRY} tentatives: {url} — {exc}")
                return None
            await asyncio.sleep(2 ** attempt)
    return None


async def fetch_session(session_url: str, source_code: str) -> dict:
    """Fetch une session complète (page principale + pagination + détails)."""
    adapter = ADAPTERS.get(source_code)
    if not adapter:
        raise ValueError(f"Adapter inconnu: {source_code}")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MezianeMonitoring/1.0)"
    }

    async with httpx.AsyncClient(headers=headers) as client:
        # Fetch page principale
        main_html = await _fetch_with_retry(client, session_url)
        if not main_html:
            raise RuntimeError(f"Impossible de fetcher la page principale: {session_url}")

        await asyncio.sleep(RATE_LIMIT_DELAY)

        # Pagination
        pagination_urls = adapter.discover_pagination(main_html, session_url)
        all_htmls = [(session_url, main_html)]

        for page_url in pagination_urls:
            html = await _fetch_with_retry(client, page_url)
            if html:
                all_htmls.append((page_url, html))
            await asyncio.sleep(RATE_LIMIT_DELAY)

        # Collecter toutes les cartes listing
        all_cards = []
        for _, html in all_htmls:
            cards = adapter.parse_listing_cards(html, session_url)
            all_cards.extend(cards)

        # Déduplication par URL
        seen = set()
        unique_cards = []
        for card in all_cards:
            if card.listing_url not in seen:
                seen.add(card.listing_url)
                unique_cards.append(card)

        # Fetch pages de détail
        listing_pages: dict[str, str] = {}
        listing_pdf_urls: dict[str, list[str]] = {}
        listing_errors: list[dict] = []

        for card in unique_cards:
            detail_html = await _fetch_with_retry(client, card.listing_url)
            if not detail_html:
                listing_errors.append({
                    "node": "hermes",
                    "detail": f"timeout fetching {card.listing_url}",
                    "ts": _now_iso(),
                })
                continue
            listing_pages[card.listing_url] = detail_html
            pdfs = adapter.discover_pdf_urls(detail_html, card.listing_url)
            if pdfs:
                listing_pdf_urls[card.listing_url] = pdfs
            await asyncio.sleep(RATE_LIMIT_DELAY)

        # Parse session metadata
        raw_session = adapter.parse_session(main_html, session_url)

        return {
            "url": session_url,
            "session_html": main_html,
            "listing_pages": listing_pages,
            "pdf_urls": listing_pdf_urls,
            "raw_session": raw_session.__dict__,
            "cards": [c.__dict__ for c in unique_cards],
            "errors": listing_errors,
        }


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
