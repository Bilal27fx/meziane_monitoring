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
                session_response = client.get(session_url)
                session_response.raise_for_status()
                session_html = session_response.text

                detail_pages: dict[str, str] = {}
                raw_sessions = self.adapter.parse_sessions(session_html, session_url)
                if raw_sessions:
                    raw_listings = self.adapter.parse_listing_cards(session_html, session_url, raw_sessions[0])
                    for raw_listing in raw_listings:
                        detail_response = client.get(raw_listing.source_url)
                        detail_response.raise_for_status()
                        detail_pages[raw_listing.source_url] = detail_response.text

                session_pages.append(
                    {
                        "url": session_url,
                        "html": session_html,
                        "detail_pages": detail_pages,
                    }
                )

        return session_pages
