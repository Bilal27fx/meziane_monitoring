# Architecture Multi-Agent LangGraph — Meziane Monitoring

**Version : 1.0 — 2026-04-11**

Ce document est la référence absolue avant toute implémentation.
Il définit le graphe d'orchestration, le state partagé, les conventions d'extension,
et l'intégration LangSmith.

---

## Principe

Le pipeline d'analyse d'enchères judiciaires est orchestré par un **StateGraph LangGraph**.
Chaque agent est un nœud indépendant avec une responsabilité unique.
Le **state** est l'unique canal de communication entre agents — aucun agent n'appelle un autre directement.

---

## Graphe d'orchestration

```
START
  │
  ▼
┌──────────────────────────────────────────────┐
│  HERMES                                      │
│  Fetch HTTP + parsing Licitor                │
│  → produit : raw_listings[], pdf_urls[]      │
└─────────────────────┬────────────────────────┘
                      │
          ┌───────────┴───────────┐
          │   (en parallèle)     │
          ▼                      ▼
┌──────────────────┐   ┌──────────────────────┐
│  ARCHIVIO        │   │  MERCATO             │
│  Télécharge PDF  │   │  Prix marché DVF     │
│  + extraction    │   │  + estimation /m²    │
│  LLM par PDF     │   │  par listing         │
└────────┬─────────┘   └──────────┬───────────┘
         │                        │
         └───────────┬────────────┘
                     │  (convergence)
                     ▼
┌──────────────────────────────────────────────┐
│  ORACLE                                      │
│  Score multi-dimensionnel                    │
│  Décision : BUY / WATCH / SKIP               │
│  Justification textuelle par listing         │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│  PERSIST                                     │
│  Upsert DB (sessions, listings, extractions) │
│  Notification Telegram si éligible           │
└─────────────────────┬────────────────────────┘
                      │
                     END
```

### Fan-out ARCHIVIO via Send()

Pour N PDFs détectés par HERMES, LangGraph envoie N instances parallèles via l'API `Send()`.
Les résultats sont fusionnés automatiquement dans le state avant ORACLE.

```
HERMES → Send("archivio", {pdf_url: "A"}) → instance 1
       → Send("archivio", {pdf_url: "B"}) → instance 2
       → Send("archivio", {pdf_url: "C"}) → instance 3
       → Send("mercato",  {listings: [...]}) → MERCATO
```

---

## State partagé

```python
class AuctionGraphState(TypedDict):

    # ── Input ──────────────────────────────────────────────
    run_id: int
    source_code: str          # "licitor" | "certeurop" | ...
    session_urls: list[str]

    # ── HERMES output ──────────────────────────────────────
    raw_pages: list[dict]
    # [{url, html, detail_pages: {url: html}, pdf_urls: [str]}]
    raw_listings: list[dict]
    # [{external_id, source_url, title, reserve_price,
    #   surface_m2, city, postal_code, auction_date, ...}]

    # ── ARCHIVIO output ────────────────────────────────────
    pdf_extractions: dict[str, dict]
    # pdf_url → {surface_m2, charges, reglement, syndic, ...}

    # ── MERCATO output ─────────────────────────────────────
    price_estimates: dict[str, dict]
    # listing_url → {prix_m2_marche, source, nb_transactions, ratio_mise_a_prix}

    # ── ORACLE output ──────────────────────────────────────
    scored_listings: list[dict]
    # [{listing_url, score, decision, breakdown, justification}]

    # ── Meta (rempli par chaque nœud) ──────────────────────
    errors: list[dict]
    # [{node, detail, ts}]
    token_usage: dict[str, int]
    # {"archivio": 1240, "mercato": 380, "oracle": 2100}
    durations_ms: dict[str, int]
    # {"hermes": 4200, "archivio": 8100, "oracle": 1300}
```

**Règle** : chaque nœud ne retourne que les clés qu'il a remplies.
LangGraph fusionne les retours partiels dans le state global.

---

## Agents

| Nom | Rôle | LLM | Modèle | Fiche |
|-----|------|-----|--------|-------|
| HERMES | Fetch HTTP + parsing pages Licitor | Non | — | [HERMES.md](./HERMES.md) |
| ARCHIVIO | Download PDF + extraction données | Oui | gpt-4o-mini | [ARCHIVIO.md](./ARCHIVIO.md) |
| MERCATO | Prix marché via DVF | Optionnel | gpt-4o-mini | [MERCATO.md](./MERCATO.md) |
| ORACLE | Score + décision BUY/WATCH/SKIP | Oui | gpt-4o | [ORACLE.md](./ORACLE.md) |
| PERSIST | Upsert DB + notification | Non | — | — |

---

## Structure des fichiers

```
backend/app/agents/
├── __init__.py
│
├── graph/
│   ├── __init__.py
│   ├── state.py             # AuctionGraphState (TypedDict)
│   ├── licitor_graph.py     # Compilation StateGraph + edges
│   └── runner.py            # invoke(run_id, source_code, session_urls)
│
├── hermes/
│   ├── __init__.py
│   ├── agent.py             # hermes_node(state) → state partiel
│   ├── fetcher.py           # HTTP fetch (session + pagination + détails)
│   └── parser.py            # parse HTML → raw_listings, pdf_urls
│
├── archivio/
│   ├── __init__.py
│   ├── agent.py             # archivio_node(state) — fan-out par PDF
│   ├── downloader.py        # Téléchargement PDF
│   └── extractor.py         # LLM extraction texte PDF → données structurées
│
├── mercato/
│   ├── __init__.py
│   ├── agent.py             # mercato_node(state)
│   └── dvf_client.py        # Appel API DVF (données valeurs foncières)
│
└── oracle/
    ├── __init__.py
    ├── agent.py             # oracle_node(state)
    └── scorer.py            # Score + décision + justification

backend/app/api/
└── auction_agent_routes.py  # POST /agent/run, GET /agent/runs, etc.

backend/app/tasks/
└── auction_tasks.py         # Celery task → graph runner

backend/app/models/          # Modèles DB (sessions, listings, runs, events)
backend/app/services/        # Services DB (log, scoring, notification)

docs/agents/
├── ARCHITECTURE.md          # Ce fichier
├── HERMES.md
├── ARCHIVIO.md
├── MERCATO.md
└── ORACLE.md
```

---

## Observabilité — LangSmith

### Variables d'environnement

```bash
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=lsv2_...
LANGCHAIN_PROJECT=meziane-licitor-prod   # ou -dev / -tests
```

### Ce qui est tracé automatiquement

| Donnée | Localisation dans LangSmith |
|--------|-----------------------------|
| Graphe d'exécution nœud par nœud | Run > Graph view |
| Tokens consommés par nœud | Run > Token usage |
| Latence par nœud | Run > Timeline |
| Input / output de chaque nœud | Run > Node I/O |
| Erreurs avec traceback complet | Run > Errors |
| Replay d'un run | Run > Replay |
| Comparaison entre runs | Compare runs |

### Projets recommandés

```
meziane-licitor-dev     → développement local
meziane-licitor-prod    → production
meziane-licitor-tests   → CI / tests automatisés
```

---

## Checkpointing PostgreSQL

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(settings.DATABASE_URL)
graph = licitor_graph.compile(checkpointer=checkpointer)
```

**Bénéfices :**
- Reprise sur crash sans re-fetcher les pages Licitor
- Inspection de l'état intermédiaire à chaque étape
- Base pour human-in-the-loop (pause avant ORACLE pour validation manuelle)

---

## Scalabilité

### Horizontale — Celery workers

Chaque `run_id` = une invocation `graph.invoke()` indépendante.
L'état est isolé par `thread_id=str(run_id)`.

```
Worker 1 → graph.invoke({run_id: 42, ...}, config={"thread_id": "42"})
Worker 2 → graph.invoke({run_id: 43, ...}, config={"thread_id": "43"})
```

### Multi-source

Le `source_code` dans le state détermine quel adapter HERMES utilise.
Ajouter une nouvelle source (ex: `certeurop`) :

1. Créer `hermes/adapters/certeurop.py` implémentant `SourceAdapter`
2. Enregistrer dans `hermes/fetcher.py` : `ADAPTERS["certeurop"] = CerteuropAdapter`
3. Aucun autre fichier modifié — le graphe LangGraph est intact

### Ajout d'un nouvel agent

Pour ajouter un agent (ex: `NOTARIUS` — vérification juridique) :

1. Créer `docs/agents/NOTARIUS.md` **(toujours la doc en premier)**
2. Créer `backend/app/agents/notarius/agent.py`
3. Ajouter les clés de sortie dans `graph/state.py`
4. Brancher dans `graph/licitor_graph.py` :
   ```python
   graph.add_node("notarius", notarius_node)
   graph.add_edge("hermes", "notarius")
   graph.add_edge("notarius", "oracle")
   ```
5. Mettre à jour le tableau des agents ci-dessus et le schéma du graphe
6. Aucun autre agent modifié

---

## Gestion des erreurs par nœud

| Nœud | Comportement en cas d'erreur | Bloquant |
|------|------------------------------|----------|
| HERMES | Exception → run échoue, pas de données | Oui |
| ARCHIVIO | Erreur PDF loggée dans `state.errors`, listing traité sans PDF | Non |
| MERCATO | Erreur API loggée, listing traité sans prix marché | Non |
| ORACLE | Exception → run échoue | Oui |
| PERSIST | Exception → run échoue, rollback DB | Oui |

Format d'une erreur dans le state :
```python
{"node": "archivio", "detail": "timeout pdf download", "ts": "2026-04-11T10:00:00Z"}
```

---

## Checklist — ajout d'un agent

- [ ] `docs/agents/NOM.md` créé en premier
- [ ] `backend/app/agents/nom/agent.py` avec `nom_node(state)`
- [ ] Clés de sortie ajoutées dans `graph/state.py`
- [ ] Nœud et edges ajoutés dans `graph/licitor_graph.py`
- [ ] Tableau des agents mis à jour dans ce fichier
- [ ] Schéma du graphe mis à jour dans ce fichier
- [ ] `docs/TRACKING.md` mis à jour
