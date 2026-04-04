from app.models.agent_definition import AgentDefinition, AgentStatus, AgentType
from app.models.agent_run import AgentRun, AgentRunStatus, AgentTriggerType
from app.models.agent_run_event import AgentRunEvent
from app.models.auction_listing import AuctionListing, AuctionListingStatus
from app.models.auction_source import AuctionSource, AuctionSourceStatus
from app.services.auction_ingestion_service import execute_auction_ingestion_run


SESSION_URL = "https://www.licitor.com/ventes-judiciaires-immobilieres/tj-paris/jeudi-19-mars-2026.html"
LISTING_URL = "https://www.licitor.com/annonce/10/73/44/vente-aux-encheres/un-appartement/paris-17eme/paris/107344.html"


def _build_run(db_session, source_code: str = "licitor"):
    source = db_session.query(AuctionSource).filter(AuctionSource.code == source_code).first()
    if source is None:
        source = AuctionSource(
            code=source_code,
            name="Licitor",
            base_url="https://www.licitor.com",
            status=AuctionSourceStatus.ACTIVE,
        )
        db_session.add(source)
        db_session.flush()

    definition = db_session.query(AgentDefinition).filter(AgentDefinition.code == "licitor_ingestion").first()
    if definition is None:
        definition = AgentDefinition(
            code="licitor_ingestion",
            name="Licitor Ingestion",
            agent_type=AgentType.INGESTION,
            status=AgentStatus.ACTIVE,
        )
        db_session.add(definition)
        db_session.flush()

    run = AgentRun(
        agent_definition_id=definition.id,
        trigger_type=AgentTriggerType.MANUAL,
        status=AgentRunStatus.PENDING,
        parameter_snapshot={
            "source_code": source_code,
            "session_pages": [
                {
                    "url": SESSION_URL,
                    "html": """
                    <html>
                      <body>
                        <h1>Ventes judiciaires immobilieres - TJ Paris - jeudi 19 mars 2026</h1>
                        <p>Audience a 14h - 1 annonce</p>
                        <a href="/annonce/10/73/44/vente-aux-encheres/un-appartement/paris-17eme/paris/107344.html">
                          Un appartement - Mise a prix 380 000 EUR - 103,70 m² - Paris 17eme 75017
                        </a>
                      </body>
                    </html>
                    """,
                    "detail_pages": {
                        LISTING_URL: """
                        <html>
                          <body>
                            <h1>Un appartement a Paris 17eme</h1>
                            <p>Mise a prix : 380 000 EUR</p>
                            <p>Surface : 103,70 m²</p>
                            <p>Appartement de 4 pieces avec 2 chambres au 3eme etage avec ascenseur, balcon et cave</p>
                            <p>Bien occupe</p>
                            <p>Adresse : 12 rue de Tocqueville, 75017 Paris</p>
                            <p>Visites : mardi 10 mars 2026 de 14h a 15h au 12 rue de Tocqueville, 75017 Paris</p>
                            <a href="/pdf/ccv.pdf">CCV</a>
                          </body>
                        </html>
                        """,
                    },
                }
            ],
        },
    )
    db_session.add(run)
    db_session.commit()
    db_session.refresh(run)
    return run


def _stub_score_listing(listing, db):
    listing.score_global = 80
    listing.recommandation = "fort_potentiel"
    listing.categorie_investissement = "prioritaire"
    return True


def test_execute_auction_ingestion_run_persists_session_and_listing(db_session, monkeypatch):
    monkeypatch.setattr("app.services.auction_ingestion_service.score_listing", _stub_score_listing)
    monkeypatch.setattr("app.services.auction_ingestion_service.send_auction_listing_notification", lambda listing: True)
    run = _build_run(db_session)

    result = execute_auction_ingestion_run(db_session, run.id)

    listing = db_session.query(AuctionListing).one()
    events = db_session.query(AgentRunEvent).filter(AgentRunEvent.run_id == run.id).order_by(AgentRunEvent.id.asc()).all()
    assert result["status"] == "success"
    assert result["sessions_created"] == 1
    assert result["listings_created"] == 1
    assert result["listings_normalized"] == 1
    assert result["listings_scored"] == 1
    assert result["notifications_sent"] == 1
    assert result["data_quality"]["normalized_listings"] == 1
    assert result["data_quality"]["complete_listings"] == 1
    assert result["data_quality"]["missing_auction_date"] == 0
    assert result["data_quality"]["missing_visit_dates"] == 0
    assert result["data_quality"]["missing_visit_location"] == 0
    assert result["data_quality"]["missing_address"] == 0
    assert listing.status == AuctionListingStatus.NORMALIZED
    assert listing.listing_type == "appartement"
    assert listing.address == "12 rue de Tocqueville, 75017 Paris"
    assert listing.nb_pieces == 4
    assert listing.nb_chambres == 2
    assert listing.etage == 3
    assert listing.ascenseur is True
    assert listing.balcon is True
    assert listing.cave is True
    assert listing.property_details["room_count"] == 4
    assert listing.occupancy_status == "occupe"
    assert [event.event_type for event in events] == [
        "run_started",
        "session_page_processing_started",
        "session_page_processed",
        "run_completed",
    ]
    assert events[-1].payload["listings_normalized"] == 1
    assert events[-1].payload["data_quality"]["complete_listings"] == 1


def test_execute_auction_ingestion_run_is_idempotent_for_existing_records(db_session, monkeypatch):
    monkeypatch.setattr("app.services.auction_ingestion_service.score_listing", _stub_score_listing)
    monkeypatch.setattr("app.services.auction_ingestion_service.send_auction_listing_notification", lambda listing: True)
    first_run = _build_run(db_session)
    execute_auction_ingestion_run(db_session, first_run.id)

    second_run = _build_run(db_session, source_code="licitor")
    second_run.parameter_snapshot = {
        "source_code": "licitor",
        "session_pages": [
            {
                "url": SESSION_URL,
                "html": """
    <html>
      <body>
        <h1>Ventes judiciaires immobilieres - TJ Paris - jeudi 19 mars 2026</h1>
        <p>Audience a 14h - 1 annonce</p>
        <a href="/annonce/10/73/44/vente-aux-encheres/un-appartement/paris-17eme/paris/107344.html">
          Un appartement - Mise a prix 390 000 EUR - 103,70 m² - Paris 17eme 75017
        </a>
      </body>
    </html>
    """,
                "detail_pages": {
                    LISTING_URL: """
                    <html>
                      <body>
                        <h1>Un appartement a Paris 17eme</h1>
                        <p>Mise a prix : 380 000 EUR</p>
                        <p>Surface : 103,70 m²</p>
                        <p>Appartement de 4 pieces au 3eme etage avec ascenseur</p>
                        <p>Bien occupe</p>
                        <p>Adresse : 12 rue de Tocqueville, 75017 Paris</p>
                      </body>
                    </html>
                    """,
                },
            }
        ],
    }
    db_session.commit()

    result = execute_auction_ingestion_run(db_session, second_run.id)

    listings = db_session.query(AuctionListing).all()
    assert len(listings) == 1
    assert result["sessions_created"] == 0
    assert result["sessions_updated"] == 1
    assert result["listings_created"] == 0
    assert result["listings_updated"] == 1
    assert result["listings_scored"] == 1
    assert result["notifications_sent"] == 0
    assert listings[0].reserve_price == 380000
    assert listings[0].score_global is not None


def test_execute_auction_ingestion_run_logs_failure(db_session):
    run = _build_run(db_session)
    run.parameter_snapshot = {"source_code": "licitor", "session_pages": [{"url": SESSION_URL}]}
    db_session.commit()

    try:
        execute_auction_ingestion_run(db_session, run.id)
        assert False, "expected ValueError"
    except ValueError:
        pass

    db_session.refresh(run)
    events = db_session.query(AgentRunEvent).filter(AgentRunEvent.run_id == run.id).order_by(AgentRunEvent.id.asc()).all()
    assert run.status == AgentRunStatus.FAILED
    assert events[-1].event_type == "run_failed"
    assert events[-1].level.value == "error"


def test_execute_auction_ingestion_run_fetches_session_urls_when_html_not_preloaded(db_session, monkeypatch):
    monkeypatch.setattr("app.services.auction_ingestion_service.score_listing", _stub_score_listing)
    monkeypatch.setattr("app.services.auction_ingestion_service.send_auction_listing_notification", lambda listing: True)
    run = _build_run(db_session)
    run.parameter_snapshot = {
        "source_code": "licitor",
        "session_urls": [SESSION_URL],
    }
    db_session.commit()

    def fake_build_session_pages(self, session_urls):
        assert session_urls == [SESSION_URL]
        return [
            {
                "url": SESSION_URL,
                "html": """
                <html>
                  <body>
                    <h1>Ventes judiciaires immobilieres - TJ Paris - jeudi 19 mars 2026</h1>
                    <p>Audience a 14h - 1 annonce</p>
                    <a href="/annonce/10/73/44/vente-aux-encheres/un-appartement/paris-17eme/paris/107344.html">
                      Un appartement - Mise a prix 380 000 EUR - 103,70 m² - Paris 17eme 75017
                    </a>
                  </body>
                </html>
                """,
                "detail_pages": {
                    LISTING_URL: """
                    <html>
                      <body>
                        <h1>Un appartement a Paris 17eme</h1>
                        <p>Mise a prix : 380 000 EUR</p>
                        <p>Surface : 103,70 m²</p>
                        <p>Appartement de 2 pieces en rez-de-chaussee sans ascenseur</p>
                        <p>Bien occupe</p>
                      </body>
                    </html>
                    """,
                },
            }
        ]

    monkeypatch.setattr(
        "app.services.auction_fetch_service.AuctionFetchService.build_session_pages",
        fake_build_session_pages,
    )

    result = execute_auction_ingestion_run(db_session, run.id)

    events = db_session.query(AgentRunEvent).filter(AgentRunEvent.run_id == run.id).order_by(AgentRunEvent.id.asc()).all()
    assert result["status"] == "success"
    assert [event.event_type for event in events[:2]] == ["fetch_started", "fetch_completed"]
    assert result["data_quality"]["normalized_listings"] == 1
    assert result["data_quality"]["complete_listings"] == 0
    assert result["data_quality"]["missing_visit_dates"] == 1
    assert result["data_quality"]["missing_visit_location"] == 1
    assert result["data_quality"]["missing_address"] == 1
    assert result["data_quality"]["incomplete_samples"][0]["missing_fields"] == [
        "visit_dates",
        "visit_location",
        "address",
    ]
