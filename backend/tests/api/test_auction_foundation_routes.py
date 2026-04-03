from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import auction_agent_routes, auction_listing_routes, auction_source_routes
from app.models.agent_definition import AgentDefinition, AgentStatus, AgentType
from app.models.agent_run import AgentRun, AgentRunStatus, AgentTriggerType
from app.models.agent_run_event import AgentRunEvent
from app.models.auction_listing import AuctionListing, AuctionListingStatus
from app.models.auction_session import AuctionSession, AuctionSessionStatus
from app.models.auction_source import AuctionSource, AuctionSourceStatus
from app.models.user import UserRole
from app.utils.auth import CurrentUser, get_current_user
from app.utils.db import get_db


def _build_app(db_session):
    app = FastAPI()
    app.include_router(auction_source_routes.router)
    app.include_router(auction_listing_routes.router)
    app.include_router(auction_agent_routes.router)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_current_user():
        return CurrentUser(id=1, role=UserRole.ADMIN, is_active=True)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user
    return app


def test_create_source_definition_parameter_set_and_run(db_session):
    app = _build_app(db_session)

    try:
        with TestClient(app) as client:
            source_response = client.post(
                "/api/auction-sources/",
                json={
                    "code": "licitor_paris",
                    "name": "Licitor Paris",
                    "base_url": "https://www.licitor.com",
                    "description": "Source Licitor TJ Paris",
                    "status": "active",
                },
            )
            assert source_response.status_code == 201
            assert source_response.json()["code"] == "licitor_paris"

            definition_response = client.post(
                "/api/auction-agents/definitions",
                json={
                    "code": "licitor_ingestion",
                    "name": "Licitor Ingestion",
                    "agent_type": "ingestion",
                    "description": "Collecte Licitor",
                    "status": "active",
                },
            )
            assert definition_response.status_code == 201
            definition_id = definition_response.json()["id"]

            parameter_set_response = client.post(
                "/api/auction-agents/parameter-sets",
                json={
                    "agent_definition_id": definition_id,
                    "name": "TJ Paris default",
                    "version": 1,
                    "is_default": True,
                    "parameters_json": {
                        "tribunal": "TJ Paris",
                        "batch_size": 10,
                        "max_cost_budget_per_run": 5.0,
                    },
                },
            )
            assert parameter_set_response.status_code == 201
            parameter_set_id = parameter_set_response.json()["id"]

            run_response = client.post(
                "/api/auction-agents/run",
                json={
                    "agent_definition_id": definition_id,
                    "parameter_set_id": parameter_set_id,
                    "trigger_type": "manual",
                    "parameter_overrides": {"batch_size": 5},
                    "code_version": "test-sha",
                },
            )
            assert run_response.status_code == 201
            run_payload = run_response.json()
            assert run_payload["status"] == "pending"
            assert run_payload["parameter_snapshot"]["tribunal"] == "TJ Paris"
            assert run_payload["parameter_snapshot"]["batch_size"] == 5

            list_runs = client.get("/api/auction-agents/runs")
            assert list_runs.status_code == 200
            assert len(list_runs.json()) == 1

            events_response = client.get(f"/api/auction-agents/run/{run_payload['id']}/events")
            assert events_response.status_code == 200
            assert len(events_response.json()) == 1
            assert events_response.json()[0]["event_type"] == "run_created"
    finally:
        app.dependency_overrides.clear()


def test_list_sessions_and_listings_with_filters(db_session):
    app = _build_app(db_session)

    source = AuctionSource(
        code="licitor_paris",
        name="Licitor Paris",
        base_url="https://www.licitor.com",
        status=AuctionSourceStatus.ACTIVE,
    )
    db_session.add(source)
    db_session.flush()

    session = AuctionSession(
        source_id=source.id,
        external_id="tj-paris-2026-03-19",
        tribunal="TJ Paris",
        city="Paris",
        source_url="https://www.licitor.com/session/tj-paris-2026-03-19",
        session_datetime=datetime(2026, 3, 19, 14, 0, 0),
        announced_listing_count=7,
        status=AuctionSessionStatus.DISCOVERED,
    )
    db_session.add(session)
    db_session.flush()

    db_session.add_all(
        [
            AuctionListing(
                source_id=source.id,
                session_id=session.id,
                external_id="107344",
                source_url="https://www.licitor.com/annonce/107344",
                reference_annonce="107344",
                title="Un appartement Paris 17eme",
                reserve_price=380000,
                city="Paris",
                postal_code="75017",
                surface_m2=103.70,
                nb_pieces=4,
                etage=3,
                ascenseur=True,
                balcon=True,
                property_details={"typology": "T4"},
                occupancy_status="a_verifier",
                status=AuctionListingStatus.DISCOVERED,
            ),
            AuctionListing(
                source_id=source.id,
                session_id=session.id,
                external_id="107345",
                source_url="https://www.licitor.com/annonce/107345",
                reference_annonce="107345",
                title="Un appartement Paris 16eme",
                reserve_price=950000,
                city="Paris",
                postal_code="75016",
                surface_m2=269.34,
                occupancy_status="libre",
                status=AuctionListingStatus.SHORTLISTED,
            ),
        ]
    )
    db_session.commit()

    try:
        with TestClient(app) as client:
            sessions_response = client.get("/api/auction-data/sessions", params={"source_id": source.id})
            assert sessions_response.status_code == 200
            assert len(sessions_response.json()) == 1

            listings_response = client.get(
                "/api/auction-data/listings",
                params={"session_id": session.id, "status": "shortlisted"},
            )
            assert listings_response.status_code == 200
            payload = listings_response.json()
            assert len(payload) == 1
            assert payload[0]["external_id"] == "107345"
            assert payload[0]["status"] == "shortlisted"
            all_listings_response = client.get("/api/auction-data/listings", params={"session_id": session.id})
            assert all_listings_response.status_code == 200
            full_payload = all_listings_response.json()
            enriched_listing = next(item for item in full_payload if item["external_id"] == "107344")
            assert enriched_listing["nb_pieces"] == 4
            assert enriched_listing["ascenseur"] is True
            assert enriched_listing["property_details"]["typology"] == "T4"
    finally:
        app.dependency_overrides.clear()


def test_create_agent_run_uses_default_parameter_set_when_none_selected(db_session):
    app = _build_app(db_session)

    try:
        with TestClient(app) as client:
            definition_response = client.post(
                "/api/auction-agents/definitions",
                json={
                    "code": "licitor_ingestion",
                    "name": "Licitor Ingestion",
                    "agent_type": "ingestion",
                    "status": "active",
                },
            )
            definition_id = definition_response.json()["id"]

            client.post(
                "/api/auction-agents/parameter-sets",
                json={
                    "agent_definition_id": definition_id,
                    "name": "default",
                    "version": 1,
                    "is_default": True,
                    "parameters_json": {"source_code": "licitor", "top_n": 20},
                },
            )

            run_response = client.post(
                "/api/auction-agents/run",
                json={
                    "agent_definition_id": definition_id,
                    "trigger_type": "manual",
                    "parameter_overrides": {"top_n": 5},
                },
            )
            assert run_response.status_code == 201
            payload = run_response.json()
            assert payload["parameter_snapshot"]["source_code"] == "licitor"
            assert payload["parameter_snapshot"]["top_n"] == 5
    finally:
        app.dependency_overrides.clear()


def test_dispatch_agent_run_enqueues_auction_task(db_session, monkeypatch):
    app = _build_app(db_session)

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
        parameter_snapshot={"source_code": "licitor", "session_pages": [{"url": "x", "html": "y"}]},
    )
    db_session.add(run)
    db_session.commit()

    calls = []

    def fake_delay(run_id):
        calls.append(run_id)

    monkeypatch.setattr(auction_agent_routes.run_auction_ingestion_task, "delay", fake_delay)

    try:
        with TestClient(app) as client:
            response = client.post(f"/api/auction-agents/run/{run.id}/dispatch")
            assert response.status_code == 202
            assert response.json()["dispatched"] is True
            assert calls == [run.id]

            events_response = client.get(f"/api/auction-agents/run/{run.id}/events")
            assert events_response.status_code == 200
            payload = events_response.json()
            assert [event["event_type"] for event in payload] == ["run_dispatched"]
    finally:
        app.dependency_overrides.clear()


def test_list_agent_run_events_returns_chronological_history(db_session):
    app = _build_app(db_session)

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
        status=AgentRunStatus.RUNNING,
        parameter_snapshot={"source_code": "licitor"},
    )
    db_session.add(run)
    db_session.flush()
    db_session.add_all(
        [
            AgentRunEvent(run_id=run.id, event_type="run_created", message="created"),
            AgentRunEvent(run_id=run.id, event_type="run_started", message="started"),
        ]
    )
    db_session.commit()

    try:
        with TestClient(app) as client:
            response = client.get(f"/api/auction-agents/run/{run.id}/events")
            assert response.status_code == 200
            assert [event["event_type"] for event in response.json()] == ["run_created", "run_started"]
    finally:
        app.dependency_overrides.clear()


def test_quick_launch_licitor_creates_and_dispatches_run(db_session, monkeypatch):
    app = _build_app(db_session)
    calls = []

    def fake_delay(run_id):
        calls.append(run_id)

    monkeypatch.setattr(auction_agent_routes.run_auction_ingestion_task, "delay", fake_delay)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/auction-agents/launch/licitor",
                json={
                    "audience_urls": [
                        "https://www.licitor.com/ventes-judiciaires-immobilieres/tj-paris/jeudi-19-mars-2026.html"
                    ],
                    "auto_dispatch": True,
                },
            )
            assert response.status_code == 202
            payload = response.json()
            assert payload["dispatched"] is True
            assert payload["task_name"] == "app.tasks.auction_tasks.run_auction_ingestion_task"
            assert calls == [payload["run_id"]]

            created_run = db_session.query(AgentRun).filter(AgentRun.id == payload["run_id"]).first()
            assert created_run is not None
            assert created_run.parameter_snapshot["source_code"] == "licitor"
            assert created_run.parameter_snapshot["session_urls"][0].startswith("https://www.licitor.com/")

            events_response = client.get(f"/api/auction-agents/run/{payload['run_id']}/events")
            assert events_response.status_code == 200
            event_types = [event["event_type"] for event in events_response.json()]
            assert event_types == ["run_created", "run_dispatched"]
    finally:
        app.dependency_overrides.clear()
