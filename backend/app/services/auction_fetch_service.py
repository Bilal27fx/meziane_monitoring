"""
auction_fetch_service.py - Fetch HTTP des pages auctions

Description:
Recupere les pages audience et detail pour les runs auctions lorsque les HTML
ne sont pas fournis directement dans le snapshot de parametres.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.agents.auction.adapters.base import SourceAdapter


DEFAULT_HEADERS = {
    "User-Agent": "MezianeMonitoringBot/1.0 (+https://localhost)",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


class AuctionFetchService:
    def __init__(self, adapter: SourceAdapter, timeout_seconds: float = 30.0):
        self.adapter = adapter
        self.timeout_seconds = timeout_seconds

    def build_session_pages(
        self,
        session_urls: list[str],
    ) -> list[dict[str, Any]]:
        session_pages: list[dict[str, Any]] = []

        with httpx.Client(timeout=self.timeout_seconds, follow_redirects=True, headers=DEFAULT_HEADERS) as client:
            for session_url in session_urls:
                # Fetch page 1
                first_response = client.get(session_url)
                first_response.raise_for_status()
                first_html = first_response.text

                # Suivi itératif de la pagination (prev/next) via BFS
                pages_html: dict[str, str] = {session_url: first_html}
                queue = [session_url]

                while queue:
                    current_url = queue.pop(0)
                    current_html = pages_html[current_url]
                    if hasattr(self.adapter, "discover_paginated_urls"):
                        for page_url in self.adapter.discover_paginated_urls(current_html, current_url):
                            if page_url not in pages_html:
                                page_response = client.get(page_url)
                                page_response.raise_for_status()
                                pages_html[page_url] = page_response.text
                                queue.append(page_url)

                # Collecte tous les listing URLs (dédupliqués) sur toutes les pages
                seen_listing_urls: set[str] = set()
                all_raw_listings = []
                raw_sessions_first = self.adapter.parse_sessions(first_html, session_url)
                raw_session = raw_sessions_first[0] if raw_sessions_first else None

                if raw_session:
                    for page_url, page_html in pages_html.items():
                        raw_listings = self.adapter.parse_listing_cards(page_html, page_url, raw_session)
                        for listing in raw_listings:
                            if listing.source_url not in seen_listing_urls:
                                seen_listing_urls.add(listing.source_url)
                                all_raw_listings.append(listing)

                # Fetch pages de détail pour chaque listing
                detail_pages: dict[str, str] = {}
                for raw_listing in all_raw_listings:
                    detail_response = client.get(raw_listing.source_url)
                    detail_response.raise_for_status()
                    detail_pages[raw_listing.source_url] = detail_response.text

                session_pages.append(
                    {
                        "url": session_url,
                        "html": first_html,
                        "pages_html": pages_html,
                        "detail_pages": detail_pages,
                    }
                )

        return session_pages
