# 2026-03-26 — Fondation backend auction agents

## Contexte

Le projet devait commencer a sortir du modele d'agent de prospection monolithique pour preparer une plateforme multi-agents, multi-sources et pilotable depuis le dashboard.

Avant de brancher un scraper Licitor ou une orchestration plus riche, il fallait poser un socle backend propre:

- tables dediees au domaine `auction_*`
- definitions d'agents et parameter sets versionnes
- runs traces
- endpoints minimaux de pilotage et de lecture

## Changements effectues

- creation des modeles SQLAlchemy:
  - `auction_source`
  - `auction_session`
  - `auction_listing`
  - `agent_definition`
  - `agent_parameter_set`
  - `agent_run`
- creation des schemas Pydantic du domaine dans `auction_schema.py`
- ajout des routes FastAPI:
  - `auction_source_routes.py`
  - `auction_listing_routes.py`
  - `auction_agent_routes.py`
- branchement du domaine dans:
  - `main.py`
  - `alembic/env.py`
  - `tests/conftest.py`
- ajout d'une migration Alembic initiale du domaine
- ajout de tests API cibles pour valider:
  - creation source / definition / parameter set / run
  - lecture sessions / listings avec filtres

## Fichiers impactes

- `backend/app/models/auction_source.py`
- `backend/app/models/auction_session.py`
- `backend/app/models/auction_listing.py`
- `backend/app/models/agent_definition.py`
- `backend/app/models/agent_parameter_set.py`
- `backend/app/models/agent_run.py`
- `backend/app/schemas/auction_schema.py`
- `backend/app/api/auction_source_routes.py`
- `backend/app/api/auction_listing_routes.py`
- `backend/app/api/auction_agent_routes.py`
- `backend/app/main.py`
- `backend/alembic/env.py`
- `backend/alembic/versions/f6a7b8c9d0e1_add_auction_agents_foundation.py`
- `backend/tests/conftest.py`
- `backend/tests/api/test_auction_foundation_routes.py`

## Analyse d'impact

Analyse d'impact manuelle realisee avant edition:

- `backend/app/main.py`
  - d=1: bootstrap API complet
  - risque: `MEDIUM`
- `backend/alembic/env.py`
  - d=1: autogeneration Alembic
  - risque: `LOW`
- nouveaux modeles / schemas / routes
  - pas d'appelants historiques
  - risque: `LOW`

## Tests effectues

Validation executee dans le conteneur backend:

```bash
docker-compose exec -T backend pytest tests/api/test_auction_foundation_routes.py
```

Resultat:

- `2 passed`

## Impact architectural

Le projet dispose maintenant d'un socle technique isole pour la future plateforme auctions:

- le domaine `auction_*` ne depend pas de `Opportunite` comme source primaire
- les parameter sets versionnes existent deja
- les runs traces existent deja
- les futures integrations Licitor pourront se brancher sans refonte de structure

## Suite recommandee

Prochaine tranche de travail:

- contrat `SourceAdapter`
- adapter `LicitorAuctionAdapter`
- tasks Celery `auction_tasks.py`
- ingestion audience/detail/documents
- projection shortlist vers dashboard agent
