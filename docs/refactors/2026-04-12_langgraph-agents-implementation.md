# 2026-04-12 — Implémentation pipeline multi-agent LangGraph

## Contexte

La documentation `docs/agents/ARCHITECTURE.md` et les fiches agents (HERMES, ARCHIVIO, MERCATO, ORACLE) étaient complètes. Aucun fichier Python n'existait côté `backend/app/agents/`. Ce refactor crée l'intégralité du code de production.

## Fichiers créés

### Graphe
- `backend/app/agents/graph/state.py` — `AuctionGraphState` TypedDict avec reducers Annotated pour fan-out merge
- `backend/app/agents/graph/licitor_graph.py` — `StateGraph` compilé (HERMES → [ARCHIVIO fan-out, MERCATO] → ORACLE → PERSIST)
- `backend/app/agents/graph/runner.py` — `invoke(run_id, source_code, session_urls)` avec logging events DB

### HERMES
- `backend/app/agents/hermes/fetcher.py` — HTTP fetch + adapter pattern (`SourceAdapter` Protocol, `LicitorAdapter`)
- `backend/app/agents/hermes/parser.py` — Normalisation `raw_listings` (dates, prix, encoding)
- `backend/app/agents/hermes/agent.py` — `hermes_node(state)` — bloquant si 0 listing

### ARCHIVIO
- `backend/app/agents/archivio/downloader.py` — Téléchargement PDF async avec retry
- `backend/app/agents/archivio/extractor.py` — `pdfplumber` → texte → gpt-4o-mini json_object
- `backend/app/agents/archivio/agent.py` — `archivio_node(state)` — reçoit `{pdf_url, listing_url}` via `Send()`

### MERCATO
- `backend/app/agents/mercato/dvf_client.py` — Client API DVF avec cache 24h en mémoire
- `backend/app/agents/mercato/agent.py` — `mercato_node(state)` — asyncio.gather sur tous les listings

### ORACLE
- `backend/app/agents/oracle/scorer.py` — Score déterministe 7 dimensions (0–100), deal breakers, flags
- `backend/app/agents/oracle/agent.py` — `oracle_node(state)` — LLM uniquement pour justification (gpt-4o)

### PERSIST
- `backend/app/agents/persist/agent.py` — Upsert `AuctionListing` + `AuctionSession`, résumé run, notification Twilio BUY

### Task
- `backend/app/tasks/auction_tasks.py` — `run_licitor_graph_task` Celery (référencé par `auction_agent_routes.py`)

## Décisions techniques

- **Fan-out ARCHIVIO** : via `Send("archivio", {pdf_url, listing_url})` — LangGraph dispatch N instances parallèles, merge automatique dans `pdf_extractions` via reducer `_merge_dict`
- **Checkpointing** : `MemorySaver` en dev, commentaire prêt pour `PostgresSaver` en prod (nécessite `langgraph-checkpoint-postgres`)
- **Score déterministe** : calculé en Python pur, LLM uniquement pour la prose de justification
- **SKIP sans LLM** : si deal breaker → justification template fixe, pas de call LLM

## Prochaines étapes

- Tester avec de vraies URLs Licitor
- Brancher `PostgresSaver` en prod
- Ajouter les `AgentRunEvent` par nœud (HERMES started/completed, etc.)
- Créer migration Alembic pour les nouveaux modèles si pas encore faite
