# Auction Agents Platform Plan

**Version:** 1.0  
**Date:** 2026-03-26  
**Scope initial:** Licitor -> Tribunal Judiciaire de Paris -> ventes judiciaires immobilieres  
**Cible:** plateforme multi-agents, multi-sources, pilotable depuis le dashboard, scalable et sobre en tokens

## 1. Objectif

Construire une plateforme d'agents immobiliers qui:

- collecte des annonces de ventes judiciaires
- stocke les donnees brutes et structurees
- enrichit chaque dossier avec des metadonnees investisseur
- utilise un LLM uniquement sur une shortlist
- classe les meilleures encheres selon des regles metier + analyse IA
- permet de piloter et ajuster tous les parametres depuis le dashboard
- supporte plus tard plusieurs agents et plusieurs sources sans refonte

## 2. Principes de conception

### 2.1 Principes techniques

- PostgreSQL reste la source de verite
- MinIO stocke les snapshots bruts et les annexes
- Redis + Celery orchestrent les jobs
- FastAPI expose les APIs de pilotage et de lecture
- Le LLM n'est jamais la premiere etape du pipeline
- Toute analyse IA doit etre reproductible via:
  - un snapshot d'entree
  - une version de prompt
  - une version de modele
  - une version de parametres

### 2.2 Principes produit

- ne pas traiter les encheres comme de simples `Opportunite`
- separer `collecte`, `normalisation`, `enrichissement`, `analyse`, `ranking`
- rendre tous les seuils critiques ajustables depuis le dashboard
- privilegier les calculs deterministes avant les appels LLM
- conserver une traçabilite complete de chaque run

### 2.3 Principe d'economie de tokens

- ne jamais envoyer annonce par annonce au LLM par defaut
- ne jamais envoyer le HTML complet au LLM
- ne jamais envoyer un PDF complet au LLM sauf cas exceptionnel
- parser localement d'abord
- scorer localement d'abord
- filtrer localement d'abord
- n'envoyer au LLM qu'une shortlist compacte
- batcher plusieurs dossiers dans un seul appel quand c'est pertinent
- cacher les analyses par hash d'entree

## 3. Perimetre V1

V1 doit couvrir:

- une seule source: Licitor
- un seul tribunal: TJ Paris
- une seule famille d'usage: identification de bonnes encheres
- pages audience + pages detail + documents annexes
- extraction structuree
- scoring deterministe
- shortlist pour analyse IA
- dashboard de pilotage

V1 ne doit pas couvrir:

- toutes les juridictions francaises
- toutes les sources du marche
- agent conversationnel autonome
- systeme complexe de workflow juridique
- automatisation de prise de decision finale

## 4. Stack recommande

### 4.1 Backend

- `FastAPI` pour les APIs
- `SQLAlchemy` pour le modele et les acces DB
- `Pydantic` pour validation et contrats API
- `Celery` pour les jobs asynchrones
- `Redis` pour queue, scheduling leger, locks simples

### 4.2 Stockage

- `PostgreSQL` pour toutes les donnees structurees
- `MinIO` pour:
  - HTML bruts
  - snapshots JSON
  - PDFs annexes
  - resultats OCR eventuels

### 4.3 Scraping et extraction

- `Playwright` pour les sites dynamiques ou si un rendu navigateur est necessaire
- `httpx` pour fetch simple quand possible
- `selectolax` ou `BeautifulSoup4` pour parse HTML
- `pypdf` pour extraction texte PDF
- `Tesseract` ou `OCRmyPDF` uniquement en fallback OCR

### 4.4 IA / LLM

- modele batch cheap pour triage
- modele plus fort pour deep analysis sur shortlist finale
- prompts versionnes en base ou fichiers versionnes
- cache d'analyse obligatoire

### 4.5 Frontend

- extension de la page Agent existante
- dashboard dedie:
  - configuration
  - runs
  - sessions
  - listings
  - shortlist
  - historique
  - experiments

## 5. Architecture logique

Le systeme doit etre decoupe en 6 domaines.

### 5.1 `auction_ingestion`

Responsable de:

- decouverte des audiences
- decouverte des annonces
- telechargement des pages detail
- telechargement des annexes
- snapshots bruts

### 5.2 `auction_normalization`

Responsable de:

- transformation source-specifique -> schema canonique
- harmonisation des champs
- validation minimale
- calcul de hash metier

### 5.3 `auction_enrichment`

Responsable de:

- geocodage
- estimation prix/m² local
- estimation loyer
- comparables
- distance transports
- tension locative
- enrichissements juridiques/documentaires

### 5.4 `auction_analysis`

Responsable de:

- resume IA
- extraction de risques a partir de donnees deja structurees
- strategie d'enchere
- plafond d'enchere recommande

### 5.5 `auction_ranking`

Responsable de:

- score deterministe
- score IA
- score final
- raison du classement

### 5.6 `auction_ops`

Responsable de:

- parameter sets
- runs
- scheduling
- logs
- metriques
- tableaux de bord

## 6. Pattern multi-agents recommande

Il ne faut pas un seul agent monolithique.  
Il faut plusieurs composants orchestrables.

### 6.1 Agents / workers cibles

- `SessionDiscoveryAgent`
- `ListingDiscoveryAgent`
- `ListingFetchAgent`
- `AnnexFetchAgent`
- `NormalizationAgent`
- `EnrichmentAgent`
- `RuleScoringAgent`
- `LLMAnalysisAgent`
- `RankingAgent`
- `NotificationAgent`
- `MonitoringAgent`

### 6.2 Contrat commun d'un adapter source

Chaque source doit implementer un contrat de ce type:

```python
class SourceAdapter(Protocol):
    source_code: str

    async def discover_sessions(self, config: dict) -> list[RawSession]:
        ...

    async def discover_listings(self, session: RawSession, config: dict) -> list[RawListing]:
        ...

    async def fetch_listing_detail(self, listing: RawListing, config: dict) -> RawListingDetail:
        ...

    async def fetch_documents(self, listing: RawListingDetail, config: dict) -> list[RawDocument]:
        ...

    def normalize_listing(self, listing: RawListingDetail, config: dict) -> CanonicalListing:
        ...
```

### 6.3 Premier adapter

V1 commence par:

- `LicitorAuctionAdapter`

Puis plus tard:

- autres tribunaux sur Licitor
- autres plateformes
- autres sources de veille immobiliere

## 7. Pipeline d'execution

### 7.1 Pipeline nominal

1. `discover_sessions`
2. `discover_listings`
3. `fetch_listing_detail`
4. `fetch_documents`
5. `normalize_listing`
6. `enrich_listing`
7. `score_listing_rules`
8. `batch_triage_llm`
9. `deep_analysis_llm`
10. `rank_listing`
11. `notify_shortlist`

### 7.2 Idempotence

Chaque etape doit etre idempotente via:

- `source_code`
- `external_id`
- `source_url`
- `content_hash`
- `document_checksum`

### 7.3 Reprocessing

Le systeme doit permettre:

- reanalyse LLM sans rescraper
- rescoring sans relancer extraction
- changement de prompt sans retoucher les raw snapshots
- changement de poids sans relancer le scraping

## 8. Schema de donnees recommande

### 8.1 Sources et sessions

#### `auction_sources`

- `id`
- `code`
- `name`
- `base_url`
- `status`
- `created_at`
- `updated_at`

#### `auction_sessions`

- `id`
- `source_id`
- `external_id`
- `tribunal`
- `session_datetime`
- `city`
- `region`
- `source_url`
- `announced_listing_count`
- `status`
- `raw_snapshot_id`
- `created_at`
- `updated_at`

### 8.2 Listings canonique

#### `auction_listings`

- `id`
- `source_id`
- `session_id`
- `external_id`
- `source_url`
- `status_source`
- `published_at`
- `last_seen_at`
- `title`
- `listing_type`
- `reference_annonce`
- `raw_snapshot_id`
- `normalized_hash`
- `created_at`
- `updated_at`

#### `auction_listing_assets`

- `id`
- `listing_id`
- `asset_type`
- `surface_m2`
- `nb_rooms`
- `address_line`
- `postal_code`
- `city`
- `district`
- `country`
- `floor`
- `has_cellar`
- `has_parking`
- `has_garden`
- `has_terrace`
- `occupancy_status`
- `description_short`
- `description_full`

#### `auction_listing_financials`

- `id`
- `listing_id`
- `reserve_price`
- `deposit_amount`
- `deposit_rate`
- `price_per_m2_source`
- `price_per_m2_market_min`
- `price_per_m2_market_avg`
- `price_per_m2_market_max`
- `estimated_rent`
- `estimated_works`
- `estimated_notary_fees`
- `estimated_auction_fees`
- `estimated_total_cost`

#### `auction_listing_visits`

- `id`
- `listing_id`
- `visit_start_at`
- `visit_end_at`
- `visit_notes`

#### `auction_listing_contacts`

- `id`
- `listing_id`
- `lawyer_name`
- `lawyer_firm`
- `lawyer_phone`
- `lawyer_address`
- `greffe_reference`

### 8.3 Documents et snapshots

#### `auction_documents`

- `id`
- `listing_id`
- `document_type`
- `source_url`
- `storage_path`
- `mime_type`
- `checksum`
- `text_content`
- `text_hash`
- `ocr_status`
- `created_at`

#### `auction_raw_snapshots`

- `id`
- `source_id`
- `snapshot_type`
- `source_url`
- `storage_path`
- `content_hash`
- `http_status`
- `fetched_at`

### 8.4 Enrichissements et analyses

#### `auction_enrichments`

- `id`
- `listing_id`
- `geocode_lat`
- `geocode_lng`
- `estimated_monthly_rent`
- `estimated_rent_yield_gross`
- `estimated_rent_yield_net`
- `estimated_resale_liquidity_score`
- `district_score`
- `transport_score`
- `comparable_count`
- `comparable_snapshot`
- `created_at`

#### `auction_llm_analyses`

- `id`
- `listing_id`
- `analysis_level`
- `model_name`
- `prompt_version`
- `input_hash`
- `summary`
- `strengths`
- `risks`
- `recommended_strategy`
- `recommended_bid_ceiling`
- `confidence_score`
- `token_input`
- `token_output`
- `cost_estimate`
- `created_at`

#### `auction_scores`

- `id`
- `listing_id`
- `scoring_version`
- `score_rules`
- `score_llm`
- `score_final`
- `score_rentability`
- `score_location`
- `score_legal_risk`
- `score_occupancy_risk`
- `score_document_quality`
- `score_work_risk`
- `score_commentary`
- `created_at`

### 8.5 Operations et pilotage

#### `agent_definitions`

- `id`
- `code`
- `name`
- `agent_type`
- `status`
- `description`

#### `agent_parameter_sets`

- `id`
- `agent_definition_id`
- `name`
- `version`
- `is_default`
- `parameters_json`
- `created_at`
- `updated_at`

#### `agent_runs`

- `id`
- `agent_definition_id`
- `parameter_set_id`
- `trigger_type`
- `status`
- `parameter_snapshot`
- `prompt_snapshot`
- `code_version`
- `started_at`
- `finished_at`

#### `agent_run_metrics`

- `id`
- `run_id`
- `sessions_discovered`
- `listings_discovered`
- `listings_normalized`
- `listings_shortlisted`
- `listings_deep_analyzed`
- `tokens_input`
- `tokens_output`
- `estimated_cost`
- `errors_count`

#### `agent_run_events`

- `id`
- `run_id`
- `stage`
- `level`
- `message`
- `payload_json`
- `created_at`

## 9. Metadonnees Licitor a capturer des la V1

### 9.1 Audience

- tribunal
- date / heure
- URL audience
- nombre d'annonces

### 9.2 Annonce detail

- numero Licitor
- date de publication
- type de bien
- description du bien
- surface
- pieces
- cave
- parking
- jardin / terrasse
- adresse
- arrondissement / ville
- statut d'occupation
- mise a prix
- consignation
- visite
- avocat
- cabinet
- telephone
- reference greffe
- liens annexes
- prix min / moyen / max au m2 si presents
- compteurs visibles du site si exploitables

### 9.3 Documents annexes

- cahier des conditions de vente
- PV descriptif
- certificat de superficie
- autres pieces si disponibles

## 10. Strategie d'economie de tokens

### 10.1 Règles

- aucune annonce brute n'est envoyee seule au LLM par defaut
- tous les HTML sont parses localement
- tous les PDFs sont parses localement
- les facts structurants sont extraits avant appel LLM
- le LLM travaille sur des fiches compactes

### 10.2 Niveaux d'analyse

#### `L0 - deterministic`

Pas de LLM.

Utilise:

- extraction structuree
- regles de filtrage
- enrichissements
- scoring deterministe

#### `L1 - batch triage`

Un modele cheap analyse plusieurs dossiers compacts dans un seul appel.

Objectif:

- eliminer rapidement
- prioriser
- detecter quelques risques majeurs

#### `L2 - deep analysis`

Modele plus fort, reserve a un top final.

Objectif:

- produire une synthese investisseur
- expliquer le rationnel
- proposer un plafond d'enchere

### 10.3 Cache

Chaque analyse doit etre cachee via:

- `input_hash`
- `prompt_version`
- `model_name`
- `analysis_level`

Si le hash est identique, on reutilise.

### 10.4 Budget control

Le dashboard doit exposer:

- `max_tokens_budget_per_run`
- `max_cost_budget_per_run`
- `max_listings_for_triage`
- `max_listings_for_deep_analysis`
- `batch_size`
- `prompt_version`
- `triage_model`
- `deep_model`

## 11. Parametres pilotables depuis le dashboard

Les parametres ne doivent jamais etre hardcodes dans l'agent.

### 11.1 Parametres de collecte

- sources actives
- tribunaux suivis
- pages historiques a regarder
- date range
- timeout
- retries
- delai entre requetes
- concurrency
- user agent policy

### 11.2 Parametres de filtrage

- prix max
- prix min
- surface min
- nombre de pieces min
- biens occupes autorises ou non
- types de biens acceptes
- zones geographiques

### 11.3 Parametres d'enrichissement

- activer comparables
- activer geocodage
- source de loyer estime
- mode estimation travaux

### 11.4 Parametres de scoring

- poids rentabilite
- poids emplacement
- poids liquidite
- poids risque juridique
- poids occupation
- poids travaux
- poids qualite documentaire
- score min shortlist

### 11.5 Parametres IA

- modele triage
- modele deep analysis
- temperature
- prompt version
- seuil de confiance
- top N avant deep analysis

### 11.6 Parametres d'execution

- run manuel
- run planifie
- dry run
- backfill
- incremental mode

### 11.7 Parametres business

- budget max global
- budget max par SCI
- strategie cible:
  - `yield`
  - `deep_value`
  - `safe_family_office`
  - `auction_aggressive`

## 12. Resolution de configuration

Il faut un `ParameterResolver`.

Ordre de precedence:

1. global defaults
2. agent defaults
3. source defaults
4. parameter set selectionne
5. overrides du run

Chaque run doit enregistrer:

- `parameter_snapshot`
- `prompt_snapshot`
- `code_version`
- `model_version`

## 13. API backend a prevoir

### 13.1 Operations agent

- `POST /api/auction-agents/run`
- `GET /api/auction-agents/runs`
- `GET /api/auction-agents/runs/{id}`
- `POST /api/auction-agents/runs/{id}/retry`
- `POST /api/auction-agents/runs/{id}/cancel`

### 13.2 Parameter sets

- `GET /api/auction-agents/parameter-sets`
- `POST /api/auction-agents/parameter-sets`
- `PUT /api/auction-agents/parameter-sets/{id}`
- `POST /api/auction-agents/parameter-sets/{id}/clone`

### 13.3 Sessions et listings

- `GET /api/auction-sessions`
- `GET /api/auction-sessions/{id}`
- `GET /api/auction-listings`
- `GET /api/auction-listings/{id}`
- `GET /api/auction-listings/{id}/documents`
- `GET /api/auction-listings/{id}/analysis`

### 13.4 Dashboard shortlist

- `GET /api/auction-dashboard/shortlist`
- `GET /api/auction-dashboard/metrics`
- `GET /api/auction-dashboard/experiments`

## 14. Ecrans dashboard a construire

### 14.1 `Agent Control`

- bouton lancer un run
- choix du parameter set
- mode dry-run
- mode backfill
- budget tokens

### 14.2 `Runs`

- historique
- statut
- duree
- cout estime
- erreurs
- metriques de sortie

### 14.3 `Sessions`

- audiences detectees
- nouvelles audiences
- nombre d'annonces
- statut de collecte

### 14.4 `Listings`

- table filtrable
- score final
- score regles
- score IA
- statut
- docs disponibles

### 14.5 `Shortlist`

- top dossiers
- resume IA
- risques
- plafond d'enchere
- actions manuelles

### 14.6 `Parameter Sets`

- creation
- edition
- activation
- comparaison

### 14.7 `Experiments`

- comparer deux parameter sets
- comparer top dossiers
- comparer cout / valeur

## 15. Strategie d'implementation dans ce repo

### 15.1 Arborescence cible backend

```text
backend/app/
├── agents/
│   └── auction/
│       ├── adapters/
│       │   ├── base.py
│       │   └── licitor.py
│       ├── orchestrators/
│       ├── prompts/
│       └── scoring/
├── api/
│   ├── auction_agent_routes.py
│   ├── auction_listing_routes.py
│   └── auction_session_routes.py
├── models/
│   ├── auction_source.py
│   ├── auction_session.py
│   ├── auction_listing.py
│   ├── auction_document.py
│   ├── auction_score.py
│   ├── agent_definition.py
│   ├── agent_parameter_set.py
│   └── agent_run.py
├── schemas/
│   └── auction_*.py
├── services/
│   └── auction/
├── tasks/
│   └── auction_tasks.py
└── queries/
    └── auction_queries.py
```

### 15.2 Ne pas faire

- ne pas etendre directement `agent_prospection.py`
- ne pas stocker Licitor directement dans `Opportunite` comme source primaire
- ne pas mettre toute la logique dans une route HTTP
- ne pas analyser annonce par annonce avec le LLM

## 16. Roadmap

### Phase 1 - Fondation

- schema DB
- raw snapshots
- adapter Licitor
- jobs Celery
- parameter sets
- runs + logs

### Phase 2 - Intelligence metier

- enrichissements
- scoring deterministe
- shortlist dashboard

### Phase 3 - IA sobre

- batch triage LLM
- deep analysis LLM
- cache d'analyse
- budget control

### Phase 4 - Multi-sources

- autres tribunaux Licitor
- autres sources
- deduplication cross-source

## 17. Risques et garde-fous

### Risques techniques

- HTML instable
- JS dynamique
- PDF mal extraits
- OCR couteux
- erreurs de deduplication

### Risques legaux / produit

- verifier robots / CGU / cadence acceptable
- separer strictement `faits extraits` et `interpretation IA`
- ne pas laisser le LLM inventer un fait absent du dossier

### Garde-fous

- snapshots bruts systematiques
- versioning des prompts
- versioning des parameter sets
- cache
- budget tokens
- tests sur parseurs
- monitoring des erreurs de scraping

## 18. Recommandation finale

La bonne approche pour ce projet est:

- un domaine `auction_*` dedie
- une architecture multi-agents
- une orchestration par jobs
- un stockage brut + normalise
- un dashboard orienté pilotage
- une strategie LLM sobre en tokens
- un systeme de parametres versionnes et optimisables

Le premier livrable concret doit etre:

- `LicitorAuctionAdapter`
- schema DB `auction_*`
- jobs Celery du pipeline
- parameter sets pilotables
- ecran dashboard Agent pour lancer, suivre et comparer les runs
