"""
telegram_notification_service.py - Notifications Telegram

Description:
Envoie des alertes Telegram pour les annonces auctions prioritaires.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime

import httpx

from app.models.auction_listing import AuctionListing
from app.services.auction_visit_service import get_actionable_visit_datetime, get_next_visit_schedule

logger = logging.getLogger(__name__)

def _format_currency(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.0f}€".replace(",", " ")


def _format_datetime(value: datetime | None) -> str:
    if value is None:
        return "—"
    return value.strftime("%d/%m/%Y %H:%M")


def is_auction_notification_eligible(
    listing: AuctionListing,
    window_days: int = 10,
    reference: datetime | None = None,
) -> bool:  # Eligibilite: categorie cible + visite proche + pas deja notifiee pour cette visite
    next_visit_at = get_actionable_visit_datetime(listing, window_days=window_days, reference=reference)
    if next_visit_at is None:
        return False
    if listing.telegram_notified_for_visit_at == next_visit_at:
        return False
    if listing.telegram_notified and listing.telegram_notified_for_visit_at is None:
        return False
    return True


def _build_auction_message(listing: AuctionListing) -> str:
    next_visit_label = "—"
    visit_schedule = get_next_visit_schedule(listing)
    if visit_schedule is not None:
        next_visit_label = visit_schedule[0]
    return (
        "🚨 Nouvelle annonce auctions prioritaire\n\n"
        f"🏷️ {listing.title}\n"
        f"📊 Score: {listing.score_global}/100 ({listing.categorie_investissement})\n"
        f"📍 {listing.city or 'Ville inconnue'}\n"
        f"💰 Mise à prix: {_format_currency(listing.reserve_price)}\n"
        f"🎯 Prix max: {_format_currency(listing.prix_max_cible)}\n"
        f"🏦 Marché: {_format_currency(listing.valeur_marche_estimee)}\n"
        f"📅 Enchères: {_format_datetime(listing.auction_date)}\n"
        f"⚖️ Lieu: {listing.auction_location or listing.auction_tribunal or '—'}\n"
        f"👀 Visite: {next_visit_label}\n"
        f"📍 Visite lieu: {listing.visit_location or '—'}\n\n"
        f"{listing.raison_score or 'Analyse indisponible'}\n\n"
        f"🔗 {listing.source_url}"
    )


def send_auction_listing_notification(listing: AuctionListing) -> bool:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logger.warning("Variables Telegram manquantes, notification auctions non envoyée")
        return False

    try:
        response = httpx.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": _build_auction_message(listing),
                "disable_web_page_preview": False,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        logger.info("Notification Telegram auctions envoyée pour listing %s", listing.id)
        return True
    except Exception as exc:
        logger.error("Erreur notification Telegram auctions pour listing %s: %s", listing.id, exc)
        return False
