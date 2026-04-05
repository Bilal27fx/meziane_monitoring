from datetime import datetime, timedelta

from app.models.auction_listing import AuctionListing
from app.services.auction_visit_service import get_actionable_visit_datetime, get_next_visit_schedule
from app.services.telegram_notification_service import is_auction_notification_eligible


def _build_listing(**overrides):
    payload = {
        "source_id": 1,
        "session_id": 1,
        "source_url": "https://example.com/listing/1",
        "title": "Studio Paris 11eme",
        "city": "Paris",
        "postal_code": "75011",
        "categorie_investissement": "prioritaire",
        "visit_dates": [],
    }
    payload.update(overrides)
    return AuctionListing(**payload)


def test_get_next_visit_schedule_returns_earliest_future_visit():
    reference = datetime(2026, 4, 4, 9, 0, 0)
    listing = _build_listing(
        visit_dates=[
            "15/04/2026 à 14h30",
            "10 avril 2026 à 09h00",
            "01/04/2026 à 09h00",
        ]
    )

    next_visit = get_next_visit_schedule(listing, reference=reference)

    assert next_visit is not None
    assert next_visit[0] == "10 avril 2026 à 09h00"
    assert next_visit[1] == datetime(2026, 4, 10, 9, 0, 0)


def test_get_actionable_visit_datetime_rejects_visit_outside_window():
    reference = datetime(2026, 4, 4, 9, 0, 0)
    listing = _build_listing(visit_dates=["20/04/2026 à 14h00"])

    visit_at = get_actionable_visit_datetime(listing, window_days=10, reference=reference)

    assert visit_at is None


def test_is_auction_notification_eligible_rejects_same_visit_already_notified():
    reference = datetime(2026, 4, 4, 9, 0, 0)
    visit_at = reference + timedelta(days=3)
    listing = _build_listing(
        visit_dates=[visit_at.strftime("%d/%m/%Y à %Hh%M")],
        telegram_notified=True,
        telegram_notified_for_visit_at=visit_at,
    )

    assert is_auction_notification_eligible(listing, reference=reference) is False


def test_is_auction_notification_eligible_accepts_upcoming_rare_listing():
    reference = datetime(2026, 4, 4, 9, 0, 0)
    listing = _build_listing(
        categorie_investissement="opportunite_rare",
        visit_dates=["08/04/2026 à 14h00"],
    )

    assert get_actionable_visit_datetime(listing, window_days=10, reference=reference) == datetime(2026, 4, 8, 14, 0, 0)
    assert is_auction_notification_eligible(listing, reference=reference) is True
