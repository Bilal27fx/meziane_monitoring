"""
auction_ingestion_service.py - Ingestion persistante du domaine auctions

Description:
Branche les adapters sources sur la persistence SQLAlchemy avec une logique
idempotente et un format de run compatible dashboard/Celery.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.agents.auction.adapters.base import RawListing, RawSession, SourceAdapter
from app.agents.auction.adapters.licitor import LicitorAuctionAdapter
from app.models.agent_run import AgentRun, AgentRunStatus
from app.models.agent_run_event import AgentRunEventLevel
from app.models.auction_listing import AuctionListing, AuctionListingStatus
from app.models.auction_session import AuctionSession, AuctionSessionStatus
from app.models.auction_source import AuctionSource
from app.services.auction_fetch_service import AuctionFetchService
from app.services.auction_run_log_service import log_agent_run_event
from app.services.auction_scoring_service import score_listing


def build_source_adapter(source_code: str) -> SourceAdapter:
    if source_code == "licitor":
        return LicitorAuctionAdapter()
    raise ValueError(f"Source adapter non supporte: {source_code}")


class AuctionIngestionService:
    def __init__(self, db: Session, adapter: SourceAdapter):
        self.db = db
        self.adapter = adapter

    def ingest_session_page(
        self,
        source: AuctionSource,
        page_url: str,
        session_html: str,
        detail_pages: dict[str, str] | None = None,
        pages_html: dict[str, str] | None = None,
    ) -> dict[str, int]:
        detail_pages = detail_pages or {}
        counters = {
            "sessions_created": 0,
            "sessions_updated": 0,
            "listings_created": 0,
            "listings_updated": 0,
            "listings_normalized": 0,
            "listings_scored": 0,
        }

        raw_sessions = self.adapter.parse_sessions(session_html, page_url)
        for raw_session in raw_sessions:
            session, session_created = self._upsert_session(source, raw_session)
            counters["sessions_created" if session_created else "sessions_updated"] += 1

            html_sources = list(pages_html.items()) if pages_html else [(page_url, session_html)]
            seen_listing_urls: set[str] = set()
            for ph_url, ph_html in html_sources:
                for raw_listing in self.adapter.parse_listing_cards(ph_html, ph_url, raw_session):
                    if raw_listing.source_url in seen_listing_urls:
                        continue
                    seen_listing_urls.add(raw_listing.source_url)
                    listing, listing_created = self._upsert_listing(source, session, raw_listing)
                    counters["listings_created" if listing_created else "listings_updated"] += 1

                    detail_html = detail_pages.get(listing.source_url)
                    if detail_html:
                        detail = self.adapter.parse_listing_detail(detail_html, listing.source_url, raw_listing)
                        self._apply_listing_detail(listing, detail.facts)
                        counters["listings_normalized"] += 1

                        if listing.score_global is None:
                            scored = score_listing(listing, self.db)
                            if scored:
                                counters["listings_scored"] += 1

        self.db.commit()
        return counters

    def _upsert_session(self, source: AuctionSource, raw_session: RawSession) -> tuple[AuctionSession, bool]:
        session = (
            self.db.query(AuctionSession)
            .filter(AuctionSession.source_id == source.id, AuctionSession.source_url == raw_session.source_url)
            .first()
        )
        created = session is None
        if created:
            session = AuctionSession(
                source_id=source.id,
                external_id=raw_session.external_id,
                tribunal=raw_session.tribunal,
                city=raw_session.city,
                source_url=raw_session.source_url,
                session_datetime=raw_session.session_datetime,
                announced_listing_count=raw_session.announced_listing_count,
                status=AuctionSessionStatus.FETCHED,
            )
            self.db.add(session)
            self.db.flush()
            return session, True

        session.external_id = raw_session.external_id
        session.tribunal = raw_session.tribunal
        session.city = raw_session.city
        session.session_datetime = raw_session.session_datetime
        session.announced_listing_count = raw_session.announced_listing_count
        session.status = AuctionSessionStatus.FETCHED
        return session, False

    def _upsert_listing(
        self,
        source: AuctionSource,
        session: AuctionSession,
        raw_listing: RawListing,
    ) -> tuple[AuctionListing, bool]:
        listing = (
            self.db.query(AuctionListing)
            .filter(AuctionListing.source_id == source.id, AuctionListing.source_url == raw_listing.source_url)
            .first()
        )
        created = listing is None
        if created:
            listing = AuctionListing(
                source_id=source.id,
                session_id=session.id,
                external_id=raw_listing.external_id,
                source_url=raw_listing.source_url,
                reference_annonce=raw_listing.reference_annonce,
                title=raw_listing.title,
                listing_type=self._infer_listing_type(raw_listing.title),
                reserve_price=raw_listing.reserve_price,
                city=raw_listing.city,
                postal_code=raw_listing.postal_code,
                surface_m2=raw_listing.surface_m2,
                occupancy_status=raw_listing.occupancy_status,
                status=AuctionListingStatus.DISCOVERED,
                last_seen_at=datetime.utcnow(),
            )
            self.db.add(listing)
            self.db.flush()
            return listing, True

        listing.session_id = session.id
        listing.external_id = raw_listing.external_id
        listing.reference_annonce = raw_listing.reference_annonce
        listing.title = raw_listing.title
        listing.listing_type = self._infer_listing_type(raw_listing.title)
        listing.reserve_price = raw_listing.reserve_price
        listing.city = raw_listing.city
        listing.postal_code = raw_listing.postal_code
        listing.surface_m2 = raw_listing.surface_m2
        listing.occupancy_status = raw_listing.occupancy_status
        listing.last_seen_at = datetime.utcnow()
        return listing, False

    def _apply_listing_detail(self, listing: AuctionListing, facts: dict[str, Any]) -> None:
        listing.title = facts.get("title") or listing.title
        listing.reserve_price = facts.get("reserve_price") or listing.reserve_price
        listing.surface_m2 = facts.get("surface_m2") or listing.surface_m2
        listing.nb_pieces = facts.get("nb_pieces") or listing.nb_pieces
        listing.nb_chambres = facts.get("nb_chambres") or listing.nb_chambres
        listing.etage = facts.get("etage") if facts.get("etage") is not None else listing.etage
        listing.type_etage = facts.get("type_etage") or listing.type_etage
        if facts.get("ascenseur") is not None:
            listing.ascenseur = facts["ascenseur"]
        if facts.get("balcon") is not None:
            listing.balcon = facts["balcon"]
        if facts.get("terrasse") is not None:
            listing.terrasse = facts["terrasse"]
        if facts.get("cave") is not None:
            listing.cave = facts["cave"]
        if facts.get("parking") is not None:
            listing.parking = facts["parking"]
        if facts.get("box") is not None:
            listing.box = facts["box"]
        if facts.get("jardin") is not None:
            listing.jardin = facts["jardin"]
        if facts.get("property_details"):
            listing.property_details = facts["property_details"]
        listing.postal_code = facts.get("postal_code") or listing.postal_code
        listing.address = facts.get("address") or listing.address
        listing.occupancy_status = facts.get("occupancy_status") or listing.occupancy_status
        if facts.get("visit_dates"):
            listing.visit_dates = facts["visit_dates"]
        listing.status = AuctionListingStatus.NORMALIZED
        listing.last_seen_at = datetime.utcnow()

    def _infer_listing_type(self, title: str) -> str | None:
        lowered = title.lower()
        if "appartement" in lowered:
            return "appartement"
        if "maison" in lowered:
            return "maison"
        if "parking" in lowered or "box" in lowered:
            return "parking"
        return None


def execute_auction_ingestion_run(db: Session, run_id: int) -> dict[str, Any]:
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise ValueError(f"Run auctions introuvable: {run_id}")

    source_code = (run.parameter_snapshot or {}).get("source_code", "licitor")
    source = db.query(AuctionSource).filter(AuctionSource.code == source_code).first()
    if not source:
        raise ValueError(f"Source auctions introuvable: {source_code}")

    session_pages = (run.parameter_snapshot or {}).get("session_pages") or []
    adapter = build_source_adapter(source_code)
    service = AuctionIngestionService(db, adapter)
    fetch_service = AuctionFetchService(adapter)

    if not isinstance(session_pages, list):
        raise ValueError("Le parametre 'session_pages' doit etre une liste")

    if not session_pages:
        session_urls = (run.parameter_snapshot or {}).get("session_urls") or []
        if not isinstance(session_urls, list) or not session_urls:
            raise ValueError("Aucune page d'audience fournie pour le run d'ingestion")
        log_agent_run_event(
            db,
            run.id,
            "fetch_started",
            "Recuperation HTTP des pages audience Licitor",
            step="fetch",
            payload={"session_urls_count": len(session_urls)},
        )
        session_pages = fetch_service.build_session_pages(session_urls)
        log_agent_run_event(
            db,
            run.id,
            "fetch_completed",
            "Recuperation HTTP terminee",
            step="fetch",
            payload={
                "session_pages_count": len(session_pages),
                "detail_pages_count": sum(len(page.get("detail_pages") or {}) for page in session_pages),
            },
        )

    run.status = AgentRunStatus.RUNNING
    run.finished_at = None
    db.flush()
    log_agent_run_event(
        db,
        run.id,
        "run_started",
        "Run d'ingestion auctions demarre",
        step="run",
        payload={"source_code": source_code, "session_pages_count": len(session_pages)},
    )

    totals = {
        "sessions_created": 0,
        "sessions_updated": 0,
        "listings_created": 0,
        "listings_updated": 0,
        "listings_normalized": 0,
        "listings_scored": 0,
        "session_pages_processed": 0,
    }

    try:
        for page in session_pages:
            page_url = page.get("url")
            page_html = page.get("html")
            if not page_url or not page_html:
                raise ValueError("Chaque page d'audience doit fournir 'url' et 'html'")

            log_agent_run_event(
                db,
                run.id,
                "session_page_processing_started",
                "Traitement d'une page audience",
                step="session_page",
                payload={"url": page_url},
            )
            counters = service.ingest_session_page(
                source=source,
                page_url=page_url,
                session_html=page_html,
                detail_pages=page.get("detail_pages"),
                pages_html=page.get("pages_html"),
            )
            log_agent_run_event(
                db,
                run.id,
                "session_page_processed",
                "Page audience traitee",
                step="session_page",
                payload={"url": page_url, **counters},
            )
            for key, value in counters.items():
                totals[key] += value
            totals["session_pages_processed"] += 1

        run.status = AgentRunStatus.SUCCESS
        run.finished_at = datetime.utcnow()
        log_agent_run_event(
            db,
            run.id,
            "run_completed",
            "Run d'ingestion auctions termine",
            step="run",
            payload=totals,
        )
        db.commit()
        return {"run_id": run.id, "status": run.status.value, **totals}
    except Exception as exc:
        run.status = AgentRunStatus.FAILED
        run.finished_at = datetime.utcnow()
        log_agent_run_event(
            db,
            run.id,
            "run_failed",
            str(exc),
            level=AgentRunEventLevel.ERROR,
            step="run",
        )
        db.commit()
        raise
