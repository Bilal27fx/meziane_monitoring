"""
auction_agent_routes.py - Routes API pilotage des agents auctions

Description:
Endpoints pour definitions d'agents, parameter sets et runs de la plateforme auctions.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.agent_definition import AgentDefinition
from app.models.agent_definition import AgentStatus, AgentType
from app.models.agent_parameter_set import AgentParameterSet
from app.models.agent_run import AgentRun, AgentRunStatus, AgentTriggerType
from app.models.agent_run_event import AgentRunEvent
from app.models.auction_source import AuctionSource, AuctionSourceStatus
from app.schemas.auction_schema import (
    AgentDefinitionCreate,
    AgentDefinitionResponse,
    AgentParameterSetCreate,
    AgentParameterSetResponse,
    AgentRunCreate,
    AgentRunDispatchResponse,
    AgentRunEventResponse,
    AgentRunResponse,
    AuctionQuickLaunchRequest,
    AuctionQuickLaunchResponse,
)
from app.services.auction_parameter_service import resolve_agent_run_parameters
from app.services.auction_run_log_service import log_agent_run_event
from app.tasks.auction_tasks import run_auction_ingestion_task
from app.utils.auth import get_current_user
from app.utils.db import get_db

router = APIRouter(prefix="/api/auction-agents", tags=["Auction Agents"], dependencies=[Depends(get_current_user)])


@router.get("/definitions", response_model=list[AgentDefinitionResponse])
def list_agent_definitions(db: Session = Depends(get_db)):
    return db.query(AgentDefinition).order_by(AgentDefinition.id.asc()).all()


@router.post("/definitions", response_model=AgentDefinitionResponse, status_code=status.HTTP_201_CREATED)
def create_agent_definition(body: AgentDefinitionCreate, db: Session = Depends(get_db)):
    existing = db.query(AgentDefinition).filter(AgentDefinition.code == body.code).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Agent {body.code} deja existant")

    definition = AgentDefinition(
        code=body.code,
        name=body.name,
        agent_type=body.agent_type.value,
        description=body.description,
        status=body.status.value,
    )
    db.add(definition)
    db.commit()
    db.refresh(definition)
    return definition


@router.get("/parameter-sets", response_model=list[AgentParameterSetResponse])
def list_parameter_sets(
    agent_definition_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AgentParameterSet)
    if agent_definition_id is not None:
        query = query.filter(AgentParameterSet.agent_definition_id == agent_definition_id)
    return query.order_by(AgentParameterSet.id.asc()).all()


@router.post("/parameter-sets", response_model=AgentParameterSetResponse, status_code=status.HTTP_201_CREATED)
def create_parameter_set(body: AgentParameterSetCreate, db: Session = Depends(get_db)):
    definition = db.query(AgentDefinition).filter(AgentDefinition.id == body.agent_definition_id).first()
    if not definition:
        raise HTTPException(status_code=404, detail=f"Agent {body.agent_definition_id} introuvable")

    if body.is_default:
        (
            db.query(AgentParameterSet)
            .filter(AgentParameterSet.agent_definition_id == body.agent_definition_id, AgentParameterSet.is_default == True)  # noqa: E712
            .update({"is_default": False})
        )

    parameter_set = AgentParameterSet(
        agent_definition_id=body.agent_definition_id,
        name=body.name,
        version=body.version,
        is_default=body.is_default,
        parameters_json=body.parameters_json,
    )
    db.add(parameter_set)
    db.commit()
    db.refresh(parameter_set)
    return parameter_set


@router.get("/runs", response_model=list[AgentRunResponse])
def list_agent_runs(
    agent_definition_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AgentRun)
    if agent_definition_id is not None:
        query = query.filter(AgentRun.agent_definition_id == agent_definition_id)
    return query.order_by(AgentRun.started_at.desc(), AgentRun.id.desc()).all()


@router.get("/run/{run_id}/events", response_model=list[AgentRunEventResponse])
def list_agent_run_events(
    run_id: int,
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} introuvable")
    return (
        db.query(AgentRunEvent)
        .filter(AgentRunEvent.run_id == run_id)
        .order_by(AgentRunEvent.created_at.asc(), AgentRunEvent.id.asc())
        .limit(limit)
        .all()
    )


@router.post("/run", response_model=AgentRunResponse, status_code=status.HTTP_201_CREATED)
def create_agent_run(body: AgentRunCreate, db: Session = Depends(get_db)):
    definition = db.query(AgentDefinition).filter(AgentDefinition.id == body.agent_definition_id).first()
    if not definition:
        raise HTTPException(status_code=404, detail=f"Agent {body.agent_definition_id} introuvable")

    try:
        parameter_set, parameter_snapshot = resolve_agent_run_parameters(
            db=db,
            definition=definition,
            parameter_set_id=body.parameter_set_id,
            overrides=body.parameter_overrides,
        )
    except ValueError as exc:
        if body.parameter_set_id is not None and not db.query(AgentParameterSet).filter(AgentParameterSet.id == body.parameter_set_id).first():
            raise HTTPException(status_code=404, detail=f"Parameter set {body.parameter_set_id} introuvable")
        raise HTTPException(status_code=400, detail=str(exc))

    run = AgentRun(
        agent_definition_id=definition.id,
        parameter_set_id=parameter_set.id if parameter_set else None,
        trigger_type=body.trigger_type.value,
        status=AgentRunStatus.PENDING.value,
        parameter_snapshot=parameter_snapshot,
        prompt_snapshot=body.prompt_snapshot,
        code_version=body.code_version,
        started_at=datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    log_agent_run_event(
        db,
        run.id,
        "run_created",
        "Run auctions cree",
        step="run",
        payload={
            "agent_definition_id": run.agent_definition_id,
            "parameter_set_id": run.parameter_set_id,
            "trigger_type": run.trigger_type.value,
        },
    )
    db.commit()
    return run


@router.post("/run/{run_id}/dispatch", response_model=AgentRunDispatchResponse, status_code=status.HTTP_202_ACCEPTED)
def dispatch_agent_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} introuvable")
    if run.status != AgentRunStatus.PENDING:
        raise HTTPException(status_code=409, detail="Seuls les runs pending peuvent etre dispatches")

    log_agent_run_event(
        db,
        run.id,
        "run_dispatched",
        "Run auctions dispatche vers Celery",
        step="dispatch",
        payload={"task_name": "app.tasks.auction_tasks.run_auction_ingestion_task"},
    )
    db.commit()
    run_auction_ingestion_task.delay(run.id)
    return AgentRunDispatchResponse(
        run_id=run.id,
        status=run.status,
        dispatched=True,
        task_name="app.tasks.auction_tasks.run_auction_ingestion_task",
    )


@router.post("/launch/licitor", response_model=AuctionQuickLaunchResponse, status_code=status.HTTP_202_ACCEPTED)
def quick_launch_licitor_run(body: AuctionQuickLaunchRequest, db: Session = Depends(get_db)):
    # Résolution des URLs : body en priorité, sinon parameter set default
    session_urls = list(body.audience_urls)
    if not session_urls:
        definition_check = db.query(AgentDefinition).filter(AgentDefinition.code == body.agent_code).first()
        if definition_check:
            default_ps = (
                db.query(AgentParameterSet)
                .filter(
                    AgentParameterSet.agent_definition_id == definition_check.id,
                    AgentParameterSet.is_default == True,  # noqa: E712
                )
                .first()
            )
            if default_ps:
                session_urls = (default_ps.parameters_json or {}).get("session_urls", [])

    if not session_urls:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Aucune URL d'audience fournie. "
                "Passez audience_urls dans le body ou configurez un AgentParameterSet "
                f"is_default=true pour l'agent '{body.agent_code}'."
            ),
        )

    source = db.query(AuctionSource).filter(AuctionSource.code == body.source_code).first()
    if source is None:
        source = AuctionSource(
            code=body.source_code,
            name="Licitor",
            base_url="https://www.licitor.com",
            status=AuctionSourceStatus.ACTIVE,
            description="Source Licitor pour ventes judiciaires immobilieres",
        )
        db.add(source)
        db.flush()

    definition = db.query(AgentDefinition).filter(AgentDefinition.code == body.agent_code).first()
    if definition is None:
        definition = AgentDefinition(
            code=body.agent_code,
            name="Licitor Ingestion",
            agent_type=AgentType.INGESTION,
            status=AgentStatus.ACTIVE,
            description="Ingestion Licitor depuis URLs d'audience",
        )
        db.add(definition)
        db.flush()

    run = AgentRun(
        agent_definition_id=definition.id,
        trigger_type=AgentTriggerType.MANUAL,
        status=AgentRunStatus.PENDING.value,
        parameter_snapshot={
            "source_code": body.source_code,
            "session_urls": session_urls,
        },
        started_at=datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    log_agent_run_event(
        db,
        run.id,
        "run_created",
        "Run Licitor cree depuis l'interface agent",
        step="run",
        payload={"source_code": body.source_code, "audience_urls_count": len(session_urls)},
    )

    task_name = None
    if body.auto_dispatch:
        log_agent_run_event(
            db,
            run.id,
            "run_dispatched",
            "Run Licitor dispatche vers Celery",
            step="dispatch",
            payload={"task_name": "app.tasks.auction_tasks.run_auction_ingestion_task"},
        )
        db.commit()
        run_auction_ingestion_task.delay(run.id)
        task_name = "app.tasks.auction_tasks.run_auction_ingestion_task"
    else:
        db.commit()

    return AuctionQuickLaunchResponse(
        run_id=run.id,
        dispatched=body.auto_dispatch,
        task_name=task_name,
    )


@router.post("/listings/{listing_id}/score", status_code=status.HTTP_200_OK)
def rescore_listing(listing_id: int, db: Session = Depends(get_db)):  # Relance le scoring LLM sur un listing
    from app.models.auction_listing import AuctionListing
    from app.services.auction_scoring_service import score_listing

    listing = db.query(AuctionListing).filter(AuctionListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail=f"Listing {listing_id} introuvable")

    scored = score_listing(listing, db)
    db.commit()

    if not scored:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scoring indisponible (OPENAI_API_KEY absente ou erreur LLM)",
        )

    return {
        "listing_id": listing_id,
        "score_global": listing.score_global,
        "recommandation": listing.recommandation,
        "scored_at": listing.scored_at,
    }
