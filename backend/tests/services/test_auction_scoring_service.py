import logging
from copy import deepcopy

from app.models.auction_listing import AuctionListing
from app.services.auction_scoring_service import (
    AuctionLLMUnavailableError,
    AuctionQualitativeSignals,
    _build_prompt,
    _categorie_investissement,
    _location_cluster,
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
        "reserve_price": 78000.0,
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
    assert listing.score_prix >= 65
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
    assert listing.score_prix == 0
    assert listing.bonus_strategique == 0
    assert listing.score_global < 55
    assert listing.categorie_investissement == "hors_cible"
    assert listing.recommandation == "rejeter"


def test_score_listing_prioritizes_small_premium_near_paris_property(monkeypatch, db_session):
    monkeypatch.setattr(
        "app.services.auction_scoring_service._fetch_qualitative_signals",
        lambda listing: AuctionQualitativeSignals(
            micro_localisation_bonus=5,
            qualite_bien_bonus=3,
            travaux_estimes=1500.0,
            raison_score="Test LLM",
            risques=["marche"],
        ),
    )
    listing = _build_listing(
        title="Deux pieces Boulogne",
        reserve_price=52000.0,
        city="Boulogne-Billancourt",
        postal_code="92100",
        surface_m2=20.0,
        nb_pieces=2,
        property_details={"typology": "T2", "condition_signals": ["bon_etat"]},
    )
    db_session.add(listing)
    db_session.flush()

    scored = score_listing(listing, db_session)

    assert scored is True
    assert listing.score_cible_paris_petite_surface >= 85
    assert listing.bonus_strategique >= 6
    assert listing.categorie_investissement in {"prioritaire", "opportunite_rare"}
    assert listing.recommandation == "fort_potentiel"


def test_score_listing_values_liquid_close_suburb_apartment(monkeypatch, db_session):
    monkeypatch.setattr(
        "app.services.auction_scoring_service._fetch_qualitative_signals",
        lambda listing: AuctionQualitativeSignals(
            micro_localisation_bonus=3,
            qualite_bien_bonus=1,
            travaux_estimes=2500.0,
            raison_score="Premiere couronne liquide avec sortie credible",
            risques=["verification occupation"],
        ),
    )
    listing = _build_listing(
        title="Appartement Colombes centre",
        reserve_price=89000.0,
        city="Colombes",
        postal_code="92700",
        surface_m2=24.0,
        nb_pieces=2,
        occupancy_status="libre",
        property_details={"typology": "T2", "condition_signals": ["bon_etat"]},
    )
    db_session.add(listing)
    db_session.flush()

    scored = score_listing(listing, db_session)

    assert scored is True
    assert listing.score_cible_paris_petite_surface >= 75
    assert listing.score_liquidite >= 70  # score_composition : T2 bon_etat libre
    assert listing.score_prix >= 40
    assert listing.score_global >= 55
    assert listing.categorie_investissement in {"a_etudier", "prioritaire", "opportunite_rare"}


def test_score_listing_keeps_good_asnieres_studio_in_play(monkeypatch, db_session):
    monkeypatch.setattr(
        "app.services.auction_scoring_service._fetch_qualitative_signals",
        lambda listing: AuctionQualitativeSignals(
            micro_localisation_bonus=4,
            qualite_bien_bonus=1,
            travaux_estimes=2000.0,
            raison_score="Studio liquide de premiere couronne",
            risques=["verification dossier"],
        ),
    )
    listing = _build_listing(
        title="Studio Asnieres-sur-Seine",
        reserve_price=92000.0,
        city="Asnieres-sur-Seine",
        postal_code="92600",
        surface_m2=21.0,
        nb_pieces=1,
        occupancy_status="libre",
        property_details={"typology": "STUDIO", "condition_signals": ["bon_etat"]},
    )
    db_session.add(listing)
    db_session.flush()

    scored = score_listing(listing, db_session)

    # reserve=92k, surface=21m2, ref_m2=7600 (dept 92) => ratio=(92k/21)/7600=0.576 => score_prix=65
    assert scored is True
    assert listing.score_prix >= 60
    assert listing.score_global >= 55
    assert listing.categorie_investissement in {"a_etudier", "prioritaire", "opportunite_rare"}


def test_location_cluster_distinguishes_liquid_and_solid_first_ring():
    assert _location_cluster(_build_listing(city="Asnieres-sur-Seine", postal_code="92600")) == "premiere_couronne_liquide"
    assert _location_cluster(_build_listing(city="Colombes", postal_code="92700")) == "premiere_couronne_solide"
    assert _location_cluster(_build_listing(city="Drancy", postal_code="93700")) == "idf_core"


def test_score_listing_applies_deal_breakers_and_caps_score(monkeypatch, db_session):
    monkeypatch.setattr(
        "app.services.auction_scoring_service._fetch_qualitative_signals",
        lambda listing: AuctionQualitativeSignals(
            micro_localisation_bonus=9,
            qualite_bien_bonus=6,
            travaux_estimes=0.0,
            raison_score="Test LLM",
            risques=["usage"],
        ),
    )
    listing = _build_listing(
        title="Usage de bureaux Paris 4eme",
        listing_type="bureau",
        reserve_price=250000.0,
        city="Paris 4eme",
        postal_code="75004",
        surface_m2=11.0,
        occupancy_status="inconnu",
        property_details={"typology": "STUDIO"},
    )
    db_session.add(listing)
    db_session.flush()

    scored = score_listing(listing, db_session)

    # bureau + surface<12 + cout_minimum >> valeur_prudente => score tres bas, cap 50
    assert scored is True
    assert listing.score_global <= 50
    assert listing.bonus_strategique == 0  # usage != habitation
    assert listing.categorie_investissement == "hors_cible"
    assert listing.prix_max_cible < listing.reserve_price


def test_score_listing_does_not_zero_target_apartment_on_sparse_data(monkeypatch, db_session):
    monkeypatch.setattr(
        "app.services.auction_scoring_service._fetch_qualitative_signals",
        lambda listing: AuctionQualitativeSignals(
            micro_localisation_bonus=2,
            qualite_bien_bonus=0,
            travaux_estimes=0.0,
            raison_score="Donnees prudentes mais pas redhibitoires",
            risques=["occupation a confirmer"],
        ),
    )
    listing = _build_listing(
        title="Appartement Colombes",
        reserve_price=135000.0,
        city="Colombes",
        postal_code="92700",
        surface_m2=28.0,
        nb_pieces=2,
        occupancy_status="inconnu",
        property_details={"typology": "T2"},
    )
    db_session.add(listing)
    db_session.flush()

    scored = score_listing(listing, db_session)

    assert scored is True
    assert listing.score_global > 0
    assert listing.score_global < 70
    assert listing.categorie_investissement in {"a_etudier", "hors_cible"}


def test_score_listing_logs_scoring_breakdown(monkeypatch, db_session, caplog):
    monkeypatch.setattr(
        "app.services.auction_scoring_service._fetch_qualitative_signals",
        lambda listing: AuctionQualitativeSignals(
            micro_localisation_bonus=4,
            qualite_bien_bonus=2,
            travaux_estimes=1500.0,
            raison_score="Breakdown test",
            risques=["controle"],
        ),
    )
    listing = _build_listing(city="Asnieres-sur-Seine", postal_code="92600")
    db_session.add(listing)
    db_session.flush()

    with caplog.at_level(logging.INFO, logger="app.services.auction_scoring_service"):
        scored = score_listing(listing, db_session)

    assert scored is True
    assert "Scoring breakdown listing" in caplog.text
    assert "cluster=premiere_couronne_liquide" in caplog.text
    assert "cible=" in caplog.text
    assert "prix=" in caplog.text
    assert "penalites:" in caplog.text


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


def test_build_prompt_keeps_literal_json_braces_in_template(monkeypatch):
    custom_config = deepcopy(_scoring_config())
    custom_config["llm"]["user_prompt_template"] = (
        "Annonce {title}\n"
        "{\n"
        '  "micro_localisation_bonus": "<int>",\n'
        '  "qualite_bien_bonus": "<int>"\n'
        "}\n"
        "Ville={city}"
    )
    monkeypatch.setattr("app.services.auction_scoring_service._scoring_config", lambda: custom_config)

    prompt = _build_prompt(_build_listing())

    assert "Annonce Studio Paris 11eme" in prompt
    assert '"micro_localisation_bonus": "<int>"' in prompt
    assert 'Ville=Paris 11eme' in prompt


def test_build_prompt_exposes_estimated_auction_and_conservative_value(monkeypatch):
    prompt = _build_prompt(_build_listing())

    assert "Prix estime encheres pour le scoring" in prompt
    assert "Valeur prudente retenue" in prompt
    assert "Paris n'est pas un jackpot automatique" in prompt
