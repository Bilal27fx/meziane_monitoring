from copy import deepcopy

from app.models.auction_listing import AuctionListing
from app.services.auction_scoring_service import (
    AuctionLLMUnavailableError,
    AuctionQualitativeSignals,
    _build_prompt,
    _categorie_investissement,
    _scoring_config,
    score_listing,
)


def _build_listing(**overrides):
    payload = {
        "source_id": 1,
        "session_id": 1,
        "source_url": "https://example.com/listing/1",
        "title": "Studio Paris 11eme",
        "listing_type": "appartement",
        "reserve_price": 145000.0,
        "city": "Paris 11eme",
        "postal_code": "75011",
        "surface_m2": 19.0,
        "nb_pieces": 1,
        "occupancy_status": "libre",
        "property_details": {"typology": "STUDIO", "condition_signals": ["bon_etat"]},
    }
    payload.update(overrides)
    return AuctionListing(**payload)


def test_score_listing_prioritizes_small_paris_property(monkeypatch, db_session):
    monkeypatch.setattr(
        "app.services.auction_scoring_service._fetch_qualitative_signals",
        lambda listing: AuctionQualitativeSignals(
            micro_localisation_bonus=7,
            qualite_bien_bonus=4,
            travaux_estimes=3000.0,
            raison_score="Test LLM",
            risques=["frais"],
        ),
    )
    listing = _build_listing()
    db_session.add(listing)
    db_session.flush()

    scored = score_listing(listing, db_session)

    assert scored is True
    assert listing.score_cible_paris_petite_surface >= 90
    assert listing.bonus_strategique == 10
    assert listing.score_global >= 85
    assert listing.categorie_investissement == "opportunite_rare"
    assert listing.recommandation == "fort_potentiel"
    assert listing.prix_max_cible is not None
    assert listing.prix_max_agressif is not None


def test_score_listing_penalizes_large_occupied_non_target_property(monkeypatch, db_session):
    monkeypatch.setattr(
        "app.services.auction_scoring_service._fetch_qualitative_signals",
        lambda listing: AuctionQualitativeSignals(
            micro_localisation_bonus=-4,
            qualite_bien_bonus=-6,
            travaux_estimes=18000.0,
            raison_score="Test LLM",
            risques=["travaux"],
        ),
    )
    listing = _build_listing(
        title="Grand appartement Evry",
        reserve_price=280000.0,
        city="Evry",
        postal_code="91000",
        surface_m2=62.0,
        nb_pieces=4,
        occupancy_status="occupe",
        property_details={"typology": "T4", "condition_signals": ["a_renover"]},
    )
    db_session.add(listing)
    db_session.flush()

    scored = score_listing(listing, db_session)

    assert scored is True
    assert listing.score_cible_paris_petite_surface <= 35
    assert listing.score_occupation <= 35
    assert listing.bonus_strategique == 0
    assert listing.score_global < 55
    assert listing.categorie_investissement == "hors_cible"
    assert listing.recommandation == "rejeter"


def test_score_listing_returns_false_when_llm_unavailable(monkeypatch, db_session):
    monkeypatch.setattr(
        "app.services.auction_scoring_service._fetch_qualitative_signals",
        lambda listing: (_ for _ in ()).throw(AuctionLLMUnavailableError("LLM down")),
    )
    listing = _build_listing()
    db_session.add(listing)
    db_session.flush()

    scored = score_listing(listing, db_session)

    assert scored is False
    assert listing.score_global is None


def test_category_thresholds_can_be_changed_via_json_config(monkeypatch):
    custom_config = deepcopy(_scoring_config())
    custom_config["scoring"]["category_thresholds"] = {
        "opportunite_rare": 95,
        "prioritaire": 80,
        "a_etudier": 60,
    }
    monkeypatch.setattr("app.services.auction_scoring_service._scoring_config", lambda: custom_config)

    assert _categorie_investissement(85) == "prioritaire"
    assert _categorie_investissement(79) == "a_etudier"


def test_build_prompt_uses_json_template(monkeypatch):
    custom_config = deepcopy(_scoring_config())
    custom_config["llm"]["user_prompt_template"] = "Titre={title}|Ville={city}|URL={source_url}|Target={strategy_target}"
    custom_config["scoring"]["strategy_target"] = "test-target"
    monkeypatch.setattr("app.services.auction_scoring_service._scoring_config", lambda: custom_config)

    prompt = _build_prompt(_build_listing())

    assert prompt == "Titre=Studio Paris 11eme|Ville=Paris 11eme|URL=https://example.com/listing/1|Target=test-target"
