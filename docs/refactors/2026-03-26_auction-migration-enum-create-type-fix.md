# Refactor: Auction Migration Enum Create Type Fix

Date: 2026-03-26

## Contexte

Les endpoints auctions retournaient `500` en production locale car la base
PostgreSQL n'avait pas encore les tables `agent_runs` et associees.

La tentative `alembic upgrade head` echouait sur:

- `psycopg2.errors.DuplicateObject: type "auctionsourcestatus" already exists`

Le probleme venait des migrations auctions qui:

- creaient explicitement les enums PostgreSQL avec `checkfirst=True`
- puis demandaient a `create_table(...)` de recréer implicitement les memes enums

## Changements

- correction de `backend/alembic/versions/f6a7b8c9d0e1_add_auction_agents_foundation.py`
- correction de `backend/alembic/versions/0f1e2d3c4b5a_add_agent_run_events.py`

Les colonnes enum de table utilisent maintenant des references PostgreSQL avec:

- `create_type=False`

ce qui evite la double creation apres le `create(..., checkfirst=True)`.

## Verification

Commandes executees:

```bash
docker-compose exec -T backend alembic upgrade head
docker-compose exec -T backend alembic current
```

Resultat:

- migrations appliquees avec succes
- revision courante: `0f1e2d3c4b5a (head)`

## Impact

- les tables auctions existent maintenant dans PostgreSQL
- les endpoints `/api/auction-agents/*` ne doivent plus tomber sur `UndefinedTable`
