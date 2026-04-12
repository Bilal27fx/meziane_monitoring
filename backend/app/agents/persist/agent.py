"""
agent.py - Nœud LangGraph PERSIST

Description:
Upsert DB (sessions, listings, extractions, scores).
Notification Telegram/Twilio si décision BUY.
Bloquant : rollback DB si erreur.

Dépendances:
- models.auction_session, auction_listing, agent_run
- sqlalchemy

Utilisé par:
- graph/licitor_graph.py (nœud "persist")
"""

import time
from datetime import datetime, timezone

from app.utils.db import SessionLocal
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def persist_node(state: dict) -> dict:
    """Nœud PERSIST — upsert DB + notification."""
    run_id = state["run_id"]
    source_code = state["source_code"]
    raw_listings = state.get("raw_listings", [])
    pdf_extractions = state.get("pdf_extractions", {})
    price_estimates = state.get("price_estimates", {})
    scored_listings = state.get("scored_listings", [])

    logger.info(f"[PERSIST] run_id={run_id} — {len(scored_listings)} listings à persister")
    t_start = time.time()

    scored_by_url = {s["listing_url"]: s for s in scored_listings}
    db = SessionLocal()

    try:
        _upsert_listings(db, run_id, source_code, raw_listings, pdf_extractions,
                         price_estimates, scored_by_url)
        _update_run_summary(db, run_id, scored_listings, state)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error(f"[PERSIST] Erreur DB, rollback: {exc}")
        raise
    finally:
        db.close()

    # Notifications BUY (non-bloquant)
    buy_listings = [s for s in scored_listings if s.get("decision") == "BUY"]
    if buy_listings:
        _notify_buys(buy_listings, raw_listings)

    duration_ms = int((time.time() - t_start) * 1000)
    logger.info(f"[PERSIST] run_id={run_id} persisté en {duration_ms}ms")

    return {"durations_ms": {"persist": duration_ms}}


def _upsert_listings(db, run_id: int, source_code: str, raw_listings: list,
                     pdf_extractions: dict, price_estimates: dict, scored_by_url: dict):
    from app.models.auction_listing import AuctionListing, AuctionListingStatus, AuctionDecision
    from app.models.auction_session import AuctionSession
    from app.models.auction_source import AuctionSource

    source = db.query(AuctionSource).filter(AuctionSource.code == source_code).first()
    source_id = source.id if source else None

    for listing_data in raw_listings:
        listing_url = listing_data.get("source_url", "")
        scored = scored_by_url.get(listing_url, {})

        # Upsert AuctionListing par source_url
        existing = db.query(AuctionListing).filter(
            AuctionListing.source_url == listing_url
        ).first()

        if not existing:
            existing = AuctionListing(source_url=listing_url)
            # Trouver ou créer la session
            session_id = _get_or_create_session(db, listing_data, source_id)
            existing.session_id = session_id
            db.add(existing)

        # Mise à jour champs HERMES
        existing.external_id = listing_data.get("external_id")
        existing.title = listing_data.get("title")
        existing.reserve_price = listing_data.get("reserve_price")
        existing.surface_m2 = listing_data.get("surface_m2")
        existing.city = listing_data.get("city")
        existing.postal_code = listing_data.get("postal_code")
        existing.address = listing_data.get("address")
        existing.tribunal = listing_data.get("tribunal")
        existing.visit_location = listing_data.get("visit_location")
        existing.occupancy_status = listing_data.get("occupancy_status")
        existing.nb_pieces = listing_data.get("nb_pieces")
        existing.lawyer_name = listing_data.get("lawyer_name")
        existing.lawyer_phone = listing_data.get("lawyer_phone")
        existing.amenities = listing_data.get("amenities", {})
        existing.visit_dates = listing_data.get("visit_dates", [])

        if listing_data.get("auction_date"):
            try:
                existing.auction_date = datetime.fromisoformat(listing_data["auction_date"])
            except (ValueError, TypeError):
                pass

        # Données PDF
        pdf_ext = _find_pdf_for_listing(listing_url, pdf_extractions)
        if pdf_ext:
            existing.pdf_data = pdf_ext

        # Données marché
        price_est = price_estimates.get(listing_url, {})
        if price_est and price_est.get("source") != "unavailable":
            existing.prix_m2_marche = price_est.get("prix_m2_marche")
            existing.ratio_prix = price_est.get("ratio")
            existing.market_data = price_est

        # Score ORACLE
        if scored:
            existing.score = scored.get("score")
            decision_str = scored.get("decision")
            if decision_str:
                try:
                    existing.decision = AuctionDecision(decision_str)
                except ValueError:
                    pass
            existing.score_breakdown = scored.get("breakdown", {})
            existing.justification = scored.get("justification")
            existing.deal_breakers = scored.get("deal_breakers", [])
            existing.flags = scored.get("flags", [])
            existing.status = AuctionListingStatus.SCORED

        existing.updated_at = datetime.utcnow()


def _get_or_create_session(db, listing_data: dict, source_id: int | None) -> int:
    from app.models.auction_session import AuctionSession

    tribunal = listing_data.get("tribunal", "")
    city = listing_data.get("city", "")
    source_url = listing_data.get("source_url", "")

    # Chercher une session existante par tribunal + source_url prefix
    base_url = "/".join(source_url.split("/")[:5])  # garder domaine + path racine
    session = db.query(AuctionSession).filter(
        AuctionSession.source_url.like(f"{base_url}%")
    ).first()

    if not session:
        session = AuctionSession(
            source_id=source_id or 1,
            external_id=source_url.rstrip("/").split("/")[-1],
            tribunal=tribunal,
            city=city,
            source_url=source_url,
        )
        db.add(session)
        db.flush()  # obtenir l'id avant commit

    return session.id


def _find_pdf_for_listing(listing_url: str, pdf_extractions: dict) -> dict | None:
    for _, extraction in pdf_extractions.items():
        if extraction and extraction.get("listing_url") == listing_url:
            return extraction
    return None


def _update_run_summary(db, run_id: int, scored_listings: list, state: dict):
    from app.models.agent_run import AgentRun, AgentRunStatus

    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        return

    buy_count = sum(1 for s in scored_listings if s.get("decision") == "BUY")
    watch_count = sum(1 for s in scored_listings if s.get("decision") == "WATCH")

    run.status = AgentRunStatus.SUCCESS
    run.finished_at = datetime.utcnow()
    run.result_summary = {
        "total_listings": len(state.get("raw_listings", [])),
        "scored": len(scored_listings),
        "buy": buy_count,
        "watch": watch_count,
        "skip": len(scored_listings) - buy_count - watch_count,
        "errors": len(state.get("errors", [])),
        "token_usage": state.get("token_usage", {}),
        "durations_ms": state.get("durations_ms", {}),
    }


def _notify_buys(buy_listings: list, raw_listings: list):
    """Notification Twilio/Telegram pour les BUY — non-bloquant."""
    raw_by_url = {r["source_url"]: r for r in raw_listings}

    for scored in buy_listings:
        listing_url = scored["listing_url"]
        raw = raw_by_url.get(listing_url, {})
        try:
            _send_twilio_notification(scored, raw)
        except Exception as exc:
            logger.warning(f"[PERSIST] Notification failed for {listing_url}: {exc}")


def _send_twilio_notification(scored: dict, listing: dict):
    from app.config import settings

    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN,
                settings.TWILIO_WHATSAPP_FROM, settings.TWILIO_WHATSAPP_TO]):
        return

    from twilio.rest import Client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    msg = (
        f"🏛️ *ENCHÈRE BUY* — Score {scored['score']}/100\n"
        f"{listing.get('title', 'Bien inconnu')}\n"
        f"{listing.get('city', '')} | {listing.get('surface_m2', '?')}m² | "
        f"{listing.get('reserve_price', '?')}€\n"
        f"{scored.get('justification', '')}\n"
        f"{listing.get('source_url', '')}"
    )

    client.messages.create(
        from_=settings.TWILIO_WHATSAPP_FROM,
        to=settings.TWILIO_WHATSAPP_TO,
        body=msg,
    )
    logger.info(f"[PERSIST] Notification Twilio envoyée: {listing.get('source_url')}")
