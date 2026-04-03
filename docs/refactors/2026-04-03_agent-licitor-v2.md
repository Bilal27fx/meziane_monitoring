# 2026-04-03 — Agent Licitor V2 : URLs backend + scoring LLM

**Plan source :** [plans/2026-04-03_agent-licitor-v2.md](../plans/2026-04-03_agent-licitor-v2.md)

## Changements effectués

### 1. Colonnes scoring sur `auction_listings`
Ajout de 10 colonnes LLM : `score_global`, `score_localisation`, `score_prix`, `score_potentiel`,
`loyer_estime`, `rentabilite_brute`, `raison_score`, `risques_llm`, `recommandation`, `scored_at`.

### 2. Migration Alembic
`a1b2c3d4e5f6_add_auction_listing_scoring.py` — up/down propres.

### 3. Service de scoring LLM
`auction_scoring_service.py` — envoie les métadonnées du listing à `gpt-4o-mini` via `response_format=json_object`,
valide avec Pydantic, persiste via `db.flush()`. Silencieux si `OPENAI_API_KEY` absente.

### 4. `AuctionQuickLaunchRequest.audience_urls` optionnel
`audience_urls` passe de `Field(..., min_length=1)` à `Field(default_factory=list)`.
Le endpoint résout les URLs dans l'ordre : body → `AgentParameterSet is_default=True` → 422.

### 5. Endpoint de rescoring manuel
`POST /api/auction-agents/listings/{listing_id}/score` — relance le scoring sur un listing existant.

### 6. Scoring intégré dans le pipeline d'ingestion
Après `_apply_listing_detail()`, si `score_global is None` → appel `score_listing()`.
Compteur `listings_scored` ajouté aux totaux du run et propagé dans les `AgentRunEvent`.

## Fichiers modifiés

| Fichier | Nature |
|---|---|
| `backend/app/models/auction_listing.py` | +10 colonnes scoring |
| `backend/app/schemas/auction_schema.py` | `audience_urls` optionnel + champs scoring dans `AuctionListingResponse` |
| `backend/app/api/auction_agent_routes.py` | Résolution URLs + endpoint rescoring |
| `backend/app/services/auction_ingestion_service.py` | Import + appel scoring + compteur |

## Fichiers créés

| Fichier | Rôle |
|---|---|
| `backend/app/services/auction_scoring_service.py` | Service scoring LLM |
| `backend/alembic/versions/a1b2c3d4e5f6_add_auction_listing_scoring.py` | Migration |

## Impact d=1

- `auction_ingestion_service.py` → impacté par `AuctionListing` (colonnes ajoutées, non breaking)
- `auction_listing_routes.py` → `AuctionListingResponse` enrichi (non breaking, champs optionnels)
- `auction_agent_routes.py` → `AuctionQuickLaunchRequest` modifié (rétrocompatible, `audience_urls` reste accepté)

## Tests à effectuer

1. `POST /api/auction-agents/launch/licitor` body `{}` sans parameter set configuré → 422
2. `POST /api/auction-agents/launch/licitor` body `{}` avec parameter set default → run créé
3. `POST /api/auction-agents/launch/licitor` avec `audience_urls` → ces URLs priment
4. Run complet → listings `NORMALIZED` ont `scored_at` renseigné si `OPENAI_API_KEY` présente
5. Run complet sans `OPENAI_API_KEY` → listings ingérés, `scored_at = null`, pas de crash
6. `POST /api/auction-agents/listings/{id}/score` → rescore et retourne le score
