# Refactor: Licitor Ingestion Run Foundation

Date: 2026-03-26

## Contexte

La fondation `auction_*` expose deja des modeles et des routes de pilotage, mais
elle ne permettait pas encore:

- de resoudre un parameter set par defaut pour un run
- de parser Licitor avec un comportement teste
- de persister une audience et ses annonces de facon idempotente
- de dispatcher un run auctions vers une vraie task Celery

## Changements

### 1. Adapter Licitor robuste et testable

- ajout du contrat source adapter dans `backend/app/agents/auction/adapters/base.py`
- ajout de `LicitorAuctionAdapter` dans `backend/app/agents/auction/adapters/licitor.py`
- correction du parsing `TJ Paris` via le slug de page
- support de `EUR` en plus de `€` pour la mise a prix
- support de `m2` et `m²` pour les surfaces

### 2. Resolution versionnee des parametres de run

- ajout de `backend/app/services/auction_parameter_service.py`
- un run peut maintenant heriter automatiquement du `parameter set` par defaut
- les overrides runtime restent prioritaires dans le snapshot final

### 3. Ingestion persistante et idempotente

- ajout de `backend/app/services/auction_ingestion_service.py`
- upsert des audiences `auction_sessions`
- upsert des annonces `auction_listings`
- normalisation minimale des details quand le HTML detail est fourni
- preservation de l'idempotence sur `source_id + source_url`

### 4. Execution Celery exploitable

- remplacement de la task placeholder par `run_auction_ingestion_task`
- branchement sur `execute_auction_ingestion_run(...)`
- ajout de l'endpoint `POST /api/auction-agents/run/{run_id}/dispatch`

## Impact

- le dashboard peut desormais creer un run auctions avec config resolue
- un run peut etre dispatché vers Celery sans scraping reseau encore
- l'ingestion accepte deja un payload HTML structure, utile pour tests, replay et futur fetcher

## Verification

Commande executee:

```bash
docker-compose exec -T backend pytest tests/services/test_licitor_adapter.py tests/services/test_auction_ingestion_service.py tests/api/test_auction_foundation_routes.py
```

Resultat:

- `9 passed`

## Suite logique

- ajouter un `SourceFetcher` Licitor pour recuperer les pages audience/detail
- stocker les snapshots bruts HTML/PDF en objet storage
- enrichir les runs avec metriques et erreurs persistantes
- brancher le dashboard sur le dispatch et l'historique de runs
