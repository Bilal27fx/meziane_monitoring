"""
seed.py - Initialisation des données de base au démarrage

Description:
Crée les enregistrements fondamentaux nécessaires au fonctionnement de l'application
si ils n'existent pas encore. Idempotent : safe à relancer plusieurs fois.

Dépendances:
- models/auction_source.py
- models/agent_definition.py
- models/agent_parameter_set.py

Utilisé par:
- entrypoint.sh (via seed_runner.py)
"""

from sqlalchemy.orm import Session

from app.models.agent_definition import AgentDefinition, AgentStatus, AgentType
from app.models.agent_parameter_set import AgentParameterSet
from app.models.auction_source import AuctionSource, AuctionSourceStatus


def seed_licitor_source(db: Session) -> AuctionSource:  # Crée la source Licitor si absente
    source = db.query(AuctionSource).filter(AuctionSource.code == "licitor").first()
    if source:
        return source

    source = AuctionSource(
        code="licitor",
        name="Licitor",
        base_url="https://www.licitor.com",
        status=AuctionSourceStatus.ACTIVE,
        description="Source Licitor pour ventes judiciaires immobilières",
    )
    db.add(source)
    db.flush()
    print("[seed] AuctionSource 'licitor' créée.")
    return source


def seed_licitor_agent(db: Session) -> AgentDefinition:  # Crée l'agent licitor_ingestion si absent
    definition = db.query(AgentDefinition).filter(AgentDefinition.code == "licitor_ingestion").first()
    if definition:
        return definition

    definition = AgentDefinition(
        code="licitor_ingestion",
        name="Licitor Ingestion",
        agent_type=AgentType.INGESTION,
        status=AgentStatus.ACTIVE,
        description="Ingestion Licitor depuis URLs d'audience",
    )
    db.add(definition)
    db.flush()
    print("[seed] AgentDefinition 'licitor_ingestion' créée.")
    return definition


def seed_licitor_default_parameter_set(db: Session, definition: AgentDefinition) -> None:  # Crée le parameter set default si absent
    existing = (
        db.query(AgentParameterSet)
        .filter(
            AgentParameterSet.agent_definition_id == definition.id,
            AgentParameterSet.is_default == True,  # noqa: E712
        )
        .first()
    )
    if existing:
        return

    parameter_set = AgentParameterSet(
        agent_definition_id=definition.id,
        name="Configuration par défaut",
        version=1,
        is_default=True,
        parameters_json={"session_urls": []},
    )
    db.add(parameter_set)
    print("[seed] AgentParameterSet default pour 'licitor_ingestion' créé.")


def run_seed(db: Session) -> None:  # Point d'entrée principal du seed
    print("[seed] Démarrage du seed...")
    seed_licitor_source(db)
    definition = seed_licitor_agent(db)
    seed_licitor_default_parameter_set(db, definition)
    db.commit()
    print("[seed] Seed terminé.")
