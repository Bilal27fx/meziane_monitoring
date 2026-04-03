"""
auction_schema.py - Schemas validation domaine auction agents

Description:
Schemas Pydantic pour les sources, audiences, listings et pilotage des agents auctions.

Dependances:
- pydantic
- models.auction_*
- models.agent_*

Utilise par:
- api/auction_source_routes.py
- api/auction_listing_routes.py
- api/auction_agent_routes.py
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AuctionSourceStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class AuctionSessionStatus(str, Enum):
    DISCOVERED = "discovered"
    FETCHED = "fetched"
    PROCESSED = "processed"


class AuctionListingStatus(str, Enum):
    DISCOVERED = "discovered"
    NORMALIZED = "normalized"
    ENRICHED = "enriched"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"


class AgentType(str, Enum):
    INGESTION = "ingestion"
    ENRICHMENT = "enrichment"
    ANALYSIS = "analysis"
    RANKING = "ranking"
    ORCHESTRATION = "orchestration"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class AgentRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentRunEventLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class AgentTriggerType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    BACKFILL = "backfill"


class AuctionSourceCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=120)
    base_url: str = Field(..., min_length=8, max_length=500)
    description: Optional[str] = None
    status: AuctionSourceStatus = AuctionSourceStatus.ACTIVE


class AuctionSourceResponse(AuctionSourceCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuctionSessionResponse(BaseModel):
    id: int
    source_id: int
    external_id: Optional[str] = None
    tribunal: str
    city: Optional[str] = None
    source_url: str
    session_datetime: datetime
    announced_listing_count: Optional[int] = None
    status: AuctionSessionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuctionListingResponse(BaseModel):
    id: int
    source_id: int
    session_id: int
    external_id: Optional[str] = None
    source_url: str
    reference_annonce: Optional[str] = None
    title: str
    listing_type: Optional[str] = None
    reserve_price: Optional[float] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    surface_m2: Optional[float] = None
    nb_pieces: Optional[int] = None
    nb_chambres: Optional[int] = None
    etage: Optional[int] = None
    type_etage: Optional[str] = None
    ascenseur: Optional[bool] = None
    balcon: Optional[bool] = None
    terrasse: Optional[bool] = None
    cave: Optional[bool] = None
    parking: Optional[bool] = None
    box: Optional[bool] = None
    jardin: Optional[bool] = None
    property_details: Optional[dict[str, Any]] = None
    occupancy_status: Optional[str] = None
    visit_dates: Optional[list[str]] = None
    auction_date: Optional[datetime] = None
    status: AuctionListingStatus
    published_at: Optional[datetime] = None
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime
    # Scoring LLM
    score_global: Optional[int] = None
    score_localisation: Optional[int] = None
    score_prix: Optional[int] = None
    score_potentiel: Optional[int] = None
    loyer_estime: Optional[float] = None
    rentabilite_brute: Optional[float] = None
    raison_score: Optional[str] = None
    risques_llm: Optional[list[str]] = None
    recommandation: Optional[str] = None
    scored_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentDefinitionCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=80)
    name: str = Field(..., min_length=2, max_length=160)
    agent_type: AgentType
    description: Optional[str] = None
    status: AgentStatus = AgentStatus.ACTIVE


class AgentDefinitionResponse(AgentDefinitionCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentParameterSetCreate(BaseModel):
    agent_definition_id: int
    name: str = Field(..., min_length=2, max_length=160)
    version: int = Field(1, ge=1)
    is_default: bool = False
    parameters_json: dict[str, Any] = Field(default_factory=dict)


class AgentParameterSetResponse(AgentParameterSetCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentRunCreate(BaseModel):
    agent_definition_id: int
    parameter_set_id: Optional[int] = None
    trigger_type: AgentTriggerType = AgentTriggerType.MANUAL
    parameter_overrides: dict[str, Any] = Field(default_factory=dict)
    prompt_snapshot: Optional[dict[str, Any]] = None
    code_version: Optional[str] = None


class AuctionQuickLaunchRequest(BaseModel):
    audience_urls: list[str] = Field(default_factory=list)  # vide = lire depuis AgentParameterSet default
    auto_dispatch: bool = True
    agent_code: str = "licitor_ingestion"
    source_code: str = "licitor"


class AgentRunResponse(BaseModel):
    id: int
    agent_definition_id: int
    parameter_set_id: Optional[int] = None
    trigger_type: AgentTriggerType
    status: AgentRunStatus
    parameter_snapshot: dict[str, Any]
    prompt_snapshot: Optional[dict[str, Any]] = None
    code_version: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AgentRunDispatchResponse(BaseModel):
    run_id: int
    status: AgentRunStatus
    dispatched: bool
    task_name: str


class AuctionQuickLaunchResponse(BaseModel):
    run_id: int
    dispatched: bool
    task_name: Optional[str] = None


class AgentRunEventResponse(BaseModel):
    id: int
    run_id: int
    level: AgentRunEventLevel
    step: Optional[str] = None
    event_type: str
    message: str
    payload: Optional[dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
