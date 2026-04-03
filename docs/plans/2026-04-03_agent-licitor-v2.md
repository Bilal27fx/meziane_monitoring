# Plan — Agent Licitor V2 : URLs en backend + scoring LLM

**Date :** 2026-04-03  
**Auteur :** Bilal Meziane  
**Statut :** À valider avant exécution

---

## Contexte

La plateforme a déjà un système auction complet (ingestion Licitor, runs, events, sources).
Le problème actuel : les URLs d'audience Licitor sont **passées depuis le frontend à chaque lancement**
(`AuctionQuickLaunchRequest.audience_urls`). Il n'y a pas de persistance de ces URLs en backend.

Le deuxième manque : après ingestion, les listings ne passent **jamais par un LLM** pour scoring.
`AuctionListing` a des champs structurés (prix, surface, ville) mais aucun score IA.

**Objectif de ce plan :**
1. Stocker les URLs d'audience Licitor dans le backend (`AgentParameterSet`)
2. Le lancement depuis le frontend ne fournit plus aucune URL — il déclenche juste le run
3. Ajouter un pipeline de scoring LLM sur les listings ingérés

---

## Ce qui existe déjà (ne pas retoucher)

| Composant | État |
|---|---|
| `LicitorAuctionAdapter` — parsing HTML | Fonctionnel, stable |
| `AuctionFetchService` — fetch HTTP | Fonctionnel |
| `AuctionIngestionService` — persistance sessions + listings | Fonctionnel |
| `AgentRun` / `AgentRunEvent` — traçabilité run | Fonctionnel |
| `AgentDefinition` / `AgentParameterSet` — définitions agents | Modèles en place, à utiliser |
| `AuctionSource` — source avec `base_url` | En place (`code="licitor"`) |
| `auction_agent_routes.py` — endpoints agents | Fonctionnel |
| `run_auction_ingestion_task` — task Celery | Fonctionnelle |

---

## Périmètre des changements

### Fichiers modifiés

| Fichier | Changement |
|---|---|
| `backend/app/api/auction_agent_routes.py` | Modifier `quick_launch_licitor_run` : ne plus exiger `audience_urls` dans le body, les lire depuis le `AgentParameterSet` default |
| `backend/app/schemas/auction_schema.py` | `AuctionQuickLaunchRequest` : `audience_urls` devient optionnel |
| `backend/app/services/auction_ingestion_service.py` | Ajouter étape de scoring LLM après normalisation des listings |
| `backend/app/models/auction_listing.py` | Ajouter champs scoring IA |

### Fichiers créés

| Fichier | Rôle |
|---|---|
| `backend/app/services/auction_scoring_service.py` | Scoring LLM d'un `AuctionListing` via OpenAI |
| `backend/alembic/versions/XXXX_add_auction_listing_scoring.py` | Migration : champs scoring sur `auction_listings` |

---

## Étape 1 — Stocker les URLs dans `AgentParameterSet`

Le modèle `AgentParameterSet` existe déjà avec un champ `parameters_json` (JSON libre).

La convention pour l'agent Licitor :

```json
{
  "source_code": "licitor",
  "session_urls": [
    "https://www.licitor.com/audiences/tj-paris/...",
    "https://www.licitor.com/audiences/tj-lyon/..."
  ]
}
```

**Ce qu'on fait :**
- Rien à créer en base — `AgentParameterSet` supporte déjà ça
- Le `parameter_set` marqué `is_default=true` pour l'agent Licitor est la config active
- Le lancement lit ce parameter set par défaut si le body ne contient pas d'URLs

---

## Étape 2 — Modifier `quick_launch_licitor_run`

**Fichier :** `backend/app/api/auction_agent_routes.py:203`

Comportement actuel :
```python
# Le body doit contenir audience_urls
parameter_snapshot = {
    "source_code": body.source_code,
    "session_urls": body.audience_urls,   # ← vient du frontend
}
```

Comportement cible :
```python
# 1. Si body.audience_urls fourni → on l'utilise (override ponctuel)
# 2. Sinon → on charge le AgentParameterSet is_default=True pour cet agent
#    et on lit session_urls depuis parameters_json
# 3. Si aucune URL trouvée → HTTP 422 avec message explicite
```

**Changement sur `AuctionQuickLaunchRequest` (schema) :**
```python
audience_urls: list[str] = []   # optionnel, vide = lire depuis backend
```

**Résolution des URLs (ordre de priorité) :**
1. `body.audience_urls` si non vide
2. `AgentParameterSet.is_default` pour `agent_code` → `parameters_json.session_urls`
3. Sinon : 422 `"Aucune URL d'audience configurée pour cet agent"`

---

## Étape 3 — Champs scoring sur `AuctionListing`

**Fichier :** `backend/app/models/auction_listing.py`

Ajouter les colonnes suivantes à la table `auction_listings` :

```python
# Scoring LLM
score_global        = Column(Integer, nullable=True, index=True)   # 0-100
score_localisation  = Column(Integer, nullable=True)               # 0-100
score_prix          = Column(Integer, nullable=True)               # 0-100
score_potentiel     = Column(Integer, nullable=True)               # 0-100
loyer_estime        = Column(Float, nullable=True)                 # €/mois
rentabilite_brute   = Column(Float, nullable=True)                 # %
raison_score        = Column(Text, nullable=True)
risques_llm         = Column(JSON, nullable=True)                  # list[str]
recommandation      = Column(String(30), nullable=True)            # "fort_potentiel" | "a_surveiller" | "rejeter"
scored_at           = Column(DateTime, nullable=True)
```

Migration : `XXXX_add_auction_listing_scoring.py`

---

## Étape 4 — Service de scoring LLM

**Fichier :** `backend/app/services/auction_scoring_service.py`

### 4.1 — Ce qu'on envoie au LLM

Toutes les métadonnées disponibles après normalisation :

```
- title
- reserve_price (mise à prix)
- surface_m2
- city / postal_code
- address
- occupancy_status (libre / occupé / None)
- listing_type (appartement / maison / parking)
- tribunal / session_datetime (date audience)
- source_url (pour référence)
- documents (liste PDF disponibles)
- visit_dates (mentions de visite)
```

Contexte investisseur transmis au LLM :
```
- Loyers moyens par zone (hardcodé pour Île-de-France : 25-35€/m² selon code postal)
- Décote occupation : -15% à -30% si occupé
- Frais judiciaires estimés : ~10% du prix d'adjudication
- Cible rentabilité brute : > 5%
```

### 4.2 — Format de réponse imposé

Validation Pydantic avant persistence :

```python
class AuctionScoringResult(BaseModel):
    score_global: int           # 0-100
    score_localisation: int     # 0-100
    score_prix: int             # 0-100
    score_potentiel: int        # 0-100
    loyer_estime: float         # €/mois
    rentabilite_brute: float    # % brut avant charges
    raison_score: str           # explication courte (2-3 phrases)
    risques: list[str]          # liste des risques identifiés
    recommandation: str         # "fort_potentiel" | "a_surveiller" | "rejeter"
```

### 4.3 — Robustesse

- `response_format={"type": "json_object"}` (structured output OpenAI)
- Timeout 20 secondes
- Si OpenAI key absente ou erreur → `scored_at` reste None, listing conservé sans score
- Modèle : `gpt-4o-mini` (suffisant pour scoring, coût maîtrisé)
- Pas de retry — le scoring peut être relancé manuellement via un endpoint dédié

### 4.4 — Interface publique du service

```python
def score_listing(listing: AuctionListing, db: Session) -> bool:
    """Score un listing via LLM et persiste le résultat. Retourne True si scoré."""
```

---

## Étape 5 — Intégration du scoring dans le pipeline d'ingestion

**Fichier :** `backend/app/services/auction_ingestion_service.py`

Après `_apply_listing_detail()`, si le listing vient d'être créé ou normalisé et n'a pas encore de score :

```python
if detail_html:
    detail = self.adapter.parse_listing_detail(...)
    self._apply_listing_detail(listing, detail.facts)
    counters["listings_normalized"] += 1

    # Scoring LLM si listing nouveau ou sans score
    if listing.score_global is None:
        scored = score_listing(listing, self.db)
        if scored:
            counters["listings_scored"] += 1
```

Le compteur `listings_scored` est ajouté aux totaux du run et loggé dans les `AgentRunEvent`.

---

## Étape 6 — Endpoint de rescoring manuel (optionnel mais utile)

Ajouter dans `auction_agent_routes.py` :

```
POST /api/auction-agents/listings/{listing_id}/score
```

Relance le scoring LLM sur un listing spécifique (utile si le modèle a changé ou si le score est absent).

---

## Ordre d'exécution

```
1. models/auction_listing.py        — ajout colonnes scoring
2. Migration alembic                — table mise à jour
3. services/auction_scoring_service.py — nouveau service
4. schemas/auction_schema.py        — audience_urls optionnel
5. api/auction_agent_routes.py      — résolution URLs depuis backend
6. services/auction_ingestion_service.py — appel scoring post-normalisation
```

---

## Ce qu'on ne fait PAS dans ce plan

- Pas de modification du `LicitorAuctionAdapter` (parsing stable)
- Pas de modification de `AuctionFetchService` (fetch HTTP stable)
- Pas de modification frontend — le bouton "Lancer" existant continue de fonctionner, juste le payload change
- Pas de scoring pour les listings en statut `DISCOVERED` (seulement ceux passés par `NORMALIZED`)
- Pas de notification WhatsApp sur les listings (hors scope)

---

## Tests attendus après livraison

1. `POST /api/auction-agents/launch/licitor` avec body `{}` → utilise les URLs du parameter set default → run créé
2. `POST /api/auction-agents/launch/licitor` avec `audience_urls` non vide → ces URLs priment
3. `POST /api/auction-agents/launch/licitor` avec body `{}` et aucun parameter set configuré → HTTP 422
4. Après un run complet : listings `NORMALIZED` ont `score_global`, `recommandation` et `scored_at` renseignés
5. Si `OPENAI_API_KEY` absente : listings ingérés normalement, `scored_at = None`, pas de crash
6. `POST /api/auction-agents/listings/{id}/score` → rescore un listing existant

---

## Refactor doc à créer après livraison

`docs/refactors/2026-04-XX_agent_licitor_urls_backend_scoring_llm.md`
