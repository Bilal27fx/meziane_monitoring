# Refactor: Auction Run Persistent Events

Date: 2026-03-26

## Contexte

La fondation auctions permettait de creer et dispatcher des runs, mais il
restait impossible de comprendre ce que l'agent faisait en cours d'execution
depuis le dashboard ou apres coup.

Le besoin etait d'avoir une timeline persistante par run, exploitable pour:

- pilotage dashboard
- debug d'ingestion
- audit des erreurs et de la progression

## Changements

### 1. Nouveau journal persistant des runs

- ajout du modele `AgentRunEvent` dans `backend/app/models/agent_run_event.py`
- relation `AgentRun.events` ajoutee dans `backend/app/models/agent_run.py`
- migration Alembic `backend/alembic/versions/0f1e2d3c4b5a_add_agent_run_events.py`

Chaque evenement stocke:

- `run_id`
- `level`
- `step`
- `event_type`
- `message`
- `payload`
- `created_at`

### 2. Helper unique de journalisation

- ajout de `backend/app/services/auction_run_log_service.py`

Ce service ecrit a la fois:

- un evenement SQL persistant
- un log applicatif standardise

### 3. Timeline branchee dans le pipeline auctions

`backend/app/services/auction_ingestion_service.py` journalise maintenant:

- demarrage du run
- debut de traitement d'une page audience
- fin de traitement d'une page audience avec compteurs
- fin de run avec totaux
- echec de run avec message d'erreur

`backend/app/tasks/auction_tasks.py` journalise aussi:

- reception de la task Celery
- echec technique de la task si applicable

### 4. Exposition API pour le dashboard

`backend/app/api/auction_agent_routes.py` expose maintenant:

- `GET /api/auction-agents/run/{run_id}/events`

et journalise aussi:

- creation du run
- dispatch vers Celery

## Impact

- le dashboard peut maintenant afficher une timeline complete de run
- les runs auctions deviennent observables sans lire uniquement les logs conteneur
- l'historique persiste meme apres fin du worker

## Verification

Commande executee:

```bash
docker-compose exec -T backend pytest tests/services/test_auction_ingestion_service.py tests/api/test_auction_foundation_routes.py
```

Resultat:

- `8 passed`

## Limites restantes

- la migration n'a pas ete appliquee sur la base locale dans cette tranche
- il n'y a pas encore de vue frontend branchee sur l'endpoint d'evenements
- il n'y a pas encore de stockage de snapshots HTML/PDF ou de logs d'enrichissement/LLM

## Suite logique

- afficher la timeline dans le dashboard auctions
- ajouter snapshots et metriques de run
- journaliser aussi les futures phases `fetch`, `normalize`, `enrich`, `rank`
