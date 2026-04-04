# Plan directeur — Module Licitor plugin, simple et scalable

**Date :** 2026-04-04  
**Auteur :** Codex  
**Statut :** Plan d'architecture et de développement  
**Cible :** Nouveau module backend `Licitor` en mode plugin, avec collecte, normalisation LLM, persistance, scoring et stratégie d'enchère

---

## 1. Résumé

L'objectif est de reconstruire l'agent Licitor de manière professionnelle, avec un design:

- simple à lire et à maintenir
- réellement modulaire côté backend
- scalable sans sur-abstraction
- observable
- testable
- orienté données canoniques + scoring déterministe

Le pipeline cible est:

1. collecte de la page liste Licitor
2. découverte des annonces
3. récupération des pages détail
4. découpage déterministe en sections métier
5. normalisation LLM vers un JSON strict
6. validation et fusion avec les données déterministes
7. persistance en base
8. scoring d'intérêt
9. calcul de stratégie d'enchère
10. exposition API / suivi des runs

Le module doit être implémenté comme un **plugin backend autonome**, et non comme une accumulation de logique dispersée dans `main.py`.

---

## 2. Contexte repo

Le repo a déjà une intention plugin, mais elle n'est pas encore branchée jusqu'au bout:

- le contrat plugin existe dans [backend/app/plugins/base.py](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/plugins/base.py#L20)
- le registre plugin existe dans [backend/app/plugins/__init__.py](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/plugins/__init__.py#L19)
- mais l'application FastAPI continue à inclure les routes à la main dans [backend/app/main.py](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/main.py#L67)

Conclusion:

- avant de développer Licitor, il faut **rendre le mécanisme plugin réel**
- le plugin Licitor ne doit pas dépendre d'un bootstrap manuel dispersé dans `main.py`

---

## 3. Référence fonctionnelle Licitor

Source cible:

- page liste officielle Licitor Paris / Ile-de-France: https://www.licitor.com/ventes-aux-encheres-immobilieres/paris-et-ile-de-france/prochaines-ventes.html

Observation utile:

- la page liste expose des cartes très condensées avec ville, typologie synthétique et mise à prix
- la page détail contient un texte semi-structuré répétitif
- les annonces suivent un gabarit stable, avec des blocs métier reconnaissables

Exemple de structure fourni par l'utilisateur:

- tribunal
- nature de la vente
- date et heure d'enchère
- description du bien
- annexes
- occupation
- mise à prix
- localisation
- visite
- avocat / contact

Le système doit donc s'appuyer sur un **sectionnement déterministe**, puis sur un **LLM de structuration**, et non envoyer du HTML brut sans contrôle.

---

## 4. Principes de conception

### 4.1 Simplicité d'abord

On ne construit pas une plateforme multi-sources complète dès la V1.  
On construit un plugin `licitor` propre, avec seulement les abstractions minimales qui évitent un rewrite immédiat.

### 4.2 Plugin réel

Le module doit vivre dans son propre périmètre:

- routes
- modèles SQLAlchemy
- schémas Pydantic
- services
- tâches
- configuration

### 4.3 Deux vérités de données

On sépare strictement:

- la **vérité brute observée**: HTML, texte source, snapshot
- la **vérité canonique métier**: JSON normalisé et exploitable

### 4.4 Le LLM structure, il ne décide pas tout

Le LLM sert à:

- classer
- extraire
- standardiser
- détecter des signaux
- proposer des catégories et risques

Le backend garde:

- la validation finale
- le scoring final
- la stratégie d'enchère
- les règles métier

### 4.5 Persistance orientée audit

Il faut pouvoir répondre à:

- qu'a vu le scraper ?
- qu'a compris le LLM ?
- qu'a gardé la normalisation ?
- pourquoi le scoring a donné ce résultat ?

### 4.6 Idempotence

Rejouer la collecte ne doit pas dupliquer les annonces.  
Le système doit upserter par clé métier stable.

---

## 5. Décision d'architecture

### 5.1 Nom et périmètre

Le plugin recommandé est:

`backend/app/plugins/licitor/`

Pourquoi `licitor` et pas un framework générique `auction_core` dès maintenant:

- plus simple
- plus lisible
- plus rapide à livrer
- plus cohérent avec le besoin actuel

Mais les objets métiers seront conçus de façon à permettre un second connecteur plus tard sans tout refaire.

### 5.2 Décision sur la donnée brute

Les pages HTML brutes ne doivent pas être stockées entièrement en BDD.  
Elles doivent être stockées en objet storage, avec référence en base:

- plus léger
- plus scalable
- plus simple à archiver

Le projet a déjà MinIO/S3 dans la stack, donc c'est le bon support.

### 5.3 Décision sur le scoring

Le scoring ne doit pas être calculé directement par le LLM.  
Le LLM fournit:

- catégories
- risques
- signaux qualitatifs bornés
- confiance

Le backend calcule:

- score final
- prix cible
- prix max safe
- prix max agressif
- verdict d'intérêt

---

## 6. Arborescence cible du plugin

```text
backend/app/plugins/licitor/
  __init__.py
  router.py
  config.py
  models.py
  schemas.py
  repository.py
  tasks.py
  prompts/
    licitor_normalizer.md
  services/
    list_fetch_service.py
    detail_fetch_service.py
    teaser_parser.py
    section_parser.py
    llm_normalizer.py
    listing_normalizer.py
    listing_upsert_service.py
    score_service.py
    bid_strategy_service.py
    orchestration_service.py
    quality_service.py
```

### Rôle des fichiers

| Fichier | Rôle |
| --- | --- |
| `__init__.py` | déclare le plugin et ses hooks |
| `router.py` | endpoints FastAPI du module |
| `config.py` | constantes métier et réglages du plugin |
| `models.py` | tables SQLAlchemy du plugin |
| `schemas.py` | schémas API et schémas de structuration |
| `repository.py` | lecture/écriture DB, requêtes de base |
| `tasks.py` | tâches Celery du plugin |
| `teaser_parser.py` | parsing des cartes de liste |
| `section_parser.py` | découpage déterministe des pages détail |
| `llm_normalizer.py` | appel LLM et validation JSON |
| `listing_normalizer.py` | fusion deterministic + LLM |
| `listing_upsert_service.py` | idempotence et mise à jour canonique |
| `score_service.py` | scoring d'intérêt |
| `bid_strategy_service.py` | prix cible, prix max, verdict d'enchère |
| `orchestration_service.py` | pipeline complet run -> listings -> scoring |
| `quality_service.py` | complétude, confiance, états de traitement |

---

## 7. Flux global du module

### 7.1 Run de collecte

1. un run est créé
2. le système charge la page liste Licitor
3. il détecte les cartes annonces
4. il extrait les URLs détail
5. il fetch les pages détail
6. il parse les sections
7. il appelle le LLM pour structurer
8. il valide et fusionne
9. il upsert la fiche canonique
10. il calcule score et stratégie d'enchère
11. il clôture le run avec métriques

### 7.2 États d'une annonce

Proposition simple:

- `discovered`
- `detail_fetched`
- `sectioned`
- `normalized`
- `scored`
- `needs_review`
- `rejected`
- `error`

### 7.3 États d'un run

- `pending`
- `running`
- `completed`
- `completed_with_errors`
- `failed`

---

## 8. Standardisation des sections d'annonce

Chaque page détail doit être convertie en sections métier normalisées.

## 8.1 Section `auction_context`

Contient:

- tribunal
- type de vente
- date d'audience
- heure d'audience
- ville d'audience si détectable
- consignation pour enchérir
- mention "outre les charges"

Exemples de clés:

- `tribunal_name`
- `sale_type_text`
- `auction_datetime_text`
- `deposit_text`
- `extra_charges_text`

## 8.2 Section `property_summary`

Contient:

- type de bien
- surface
- nombre de pièces
- annexes
- étage / niveau
- description compacte

Clés:

- `asset_type`
- `surface_text`
- `rooms_text`
- `annexes_text`
- `level_text`
- `description_text`

## 8.3 Section `occupancy`

Contient:

- statut d'occupation
- locataire / inoccupé / occupé / à vérifier

Clés:

- `occupancy_text`
- `occupancy_status_raw`

## 8.4 Section `pricing`

Contient:

- mise à prix
- devise
- charges
- éventuelles mentions complémentaires

Clés:

- `reserve_price_text`
- `currency`
- `charges_note`

## 8.5 Section `location`

Contient:

- arrondissement / ville
- adresse
- précision plan / exactitude non garantie

Clés:

- `city_text`
- `address_text`
- `map_notice_text`

## 8.6 Section `visit`

Contient:

- date de visite
- heure début
- heure fin
- lieu si explicite

Clés:

- `visit_text`
- `visit_date_text`
- `visit_time_range_text`

## 8.7 Section `legal_contact`

Contient:

- nom de l'avocat
- adresse cabinet
- téléphone
- email si présent

Clés:

- `lawyer_name`
- `lawyer_address`
- `lawyer_phone`
- `lawyer_email`

## 8.8 Section `free_text`

Tout ce qui reste et ne doit pas être perdu:

- mentions cadastrales
- lots
- servitudes
- réserves
- éléments ambigus

---

## 9. Contrat JSON du LLM

Le LLM reçoit:

- URL source
- texte complet nettoyé
- sections déterministes
- éventuellement contexte run

Il ne reçoit pas du HTML brut sauf fallback de debug.

### 9.1 Contrat de sortie

Le LLM doit retourner un JSON strict du type:

```json
{
  "source": "licitor",
  "source_url": "https://www.licitor.com/...",
  "auction": {
    "tribunal_name": "Tribunal Judiciaire de Paris",
    "auction_datetime": "2026-05-07T14:00:00",
    "sale_type": "vente_aux_encheres_publiques",
    "deposit_required": true,
    "deposit_note": "10% du montant de la mise à prix"
  },
  "asset": {
    "asset_type": "appartement",
    "subtypes": ["cave"],
    "surface_m2": 55.0,
    "surface_source": "loi_carrez",
    "rooms_count": 2,
    "bedrooms_count": null,
    "level_label": "rez-de-chaussée",
    "occupancy_status": "vacant"
  },
  "location": {
    "city": "Paris",
    "district": "16eme",
    "postal_code": "75016",
    "address_line": "22 square de l'Alboni"
  },
  "pricing": {
    "reserve_price_eur": 140000,
    "charges_included": false
  },
  "visit": {
    "visit_slots": [
      {
        "start": "2026-04-27T12:00:00",
        "end": "2026-04-27T13:00:00"
      }
    ]
  },
  "legal_contact": {
    "lawyer_name": "Maître Florence Renault",
    "lawyer_address": "22 rue Breguet - 75011 Paris",
    "lawyer_phone": "01 42 21 06 01"
  },
  "risk_flags": [
    "occupation_inconnue",
    "adresse_a_verifier"
  ],
  "classification": {
    "asset_family": "residentiel",
    "market_segment": "appartement_paris",
    "llm_confidence": 0.88
  },
  "evidence": {
    "auction_datetime": "jeudi 7 mai 2026 à 14h",
    "reserve_price_eur": "Mise à prix : 140 000 €",
    "occupancy_status": "Inoccupé"
  }
}
```

### 9.2 Règles du prompt

Le prompt doit imposer:

- JSON uniquement
- pas d'invention
- `null` quand inconnu
- champ `evidence` obligatoire pour les champs critiques
- liste de `risk_flags` bornée
- confiance entre `0.0` et `1.0`

### 9.3 Champs critiques

Champs indispensables pour qu'une annonce soit "scorable":

- `auction.auction_datetime`
- `asset.asset_type`
- `pricing.reserve_price_eur`
- `location.city`
- au moins une information de localisation exploitable

---

## 10. Modèle de données recommandé

## 10.1 Table `licitor_ingestion_runs`

Rôle:

- tracer chaque run
- centraliser métriques et erreurs

Champs:

| Champ | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK |
| `status` | `varchar(32)` | `pending/running/completed/...` |
| `source_url` | `text` | URL de la page liste |
| `started_at` | `timestamp` | |
| `finished_at` | `timestamp null` | |
| `pages_discovered` | `int` | |
| `listing_urls_discovered` | `int` | |
| `listings_created` | `int` | |
| `listings_updated` | `int` | |
| `listings_scored` | `int` | |
| `errors_count` | `int` | |
| `config_json` | `jsonb` | paramètres du run |
| `metrics_json` | `jsonb` | résumé détaillé |
| `error_summary_json` | `jsonb` | erreurs agrégées |
| `created_at` | `timestamp` | |

Indexes:

- `idx_licitor_ingestion_runs_status`
- `idx_licitor_ingestion_runs_started_at`

## 10.2 Table `licitor_listing_snapshots`

Rôle:

- conserver la vérité brute et la vérité extraite à un instant donné
- auditer ce que le système a vu

Champs:

| Champ | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK |
| `run_id` | `bigint` | FK `licitor_ingestion_runs.id` |
| `source_url` | `text` | URL détail |
| `source_hash` | `varchar(64)` | hash stable du HTML |
| `storage_key_html` | `text` | chemin MinIO de la page brute |
| `teaser_json` | `jsonb` | données de la carte liste |
| `sections_json` | `jsonb` | sections déterministes |
| `llm_output_json` | `jsonb` | sortie brute validée |
| `normalized_json` | `jsonb` | objet fusionné |
| `quality_json` | `jsonb` | complétude / flags |
| `created_at` | `timestamp` | |

Indexes:

- `idx_licitor_listing_snapshots_run_id`
- `idx_licitor_listing_snapshots_source_url`
- `idx_licitor_listing_snapshots_source_hash`

## 10.3 Table `licitor_listings`

Rôle:

- table canonique "courante"
- une ligne par annonce active / connue

Clé d'unicité recommandée:

- `source_url` unique

Champs:

| Champ | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK |
| `current_snapshot_id` | `bigint null` | FK snapshot |
| `source_url` | `text` | unique |
| `external_ref` | `varchar(120) null` | si disponible |
| `tribunal_name` | `varchar(200) null` | |
| `auction_datetime` | `timestamp null` | |
| `sale_type` | `varchar(80) null` | |
| `asset_type` | `varchar(80) null` | |
| `asset_family` | `varchar(80) null` | |
| `surface_m2` | `numeric(10,2) null` | |
| `surface_source` | `varchar(40) null` | ex `loi_carrez` |
| `rooms_count` | `int null` | |
| `bedrooms_count` | `int null` | |
| `level_label` | `varchar(120) null` | |
| `annexes_json` | `jsonb` | cave, parking, etc. |
| `occupancy_status` | `varchar(40) null` | |
| `reserve_price_eur` | `numeric(12,2) null` | |
| `charges_note` | `text null` | |
| `city` | `varchar(120) null` | |
| `district` | `varchar(80) null` | |
| `postal_code` | `varchar(10) null` | |
| `address_line` | `text null` | |
| `visit_slots_json` | `jsonb` | |
| `lawyer_name` | `varchar(200) null` | |
| `lawyer_phone` | `varchar(40) null` | |
| `lawyer_address` | `text null` | |
| `risk_flags_json` | `jsonb` | |
| `llm_confidence` | `numeric(4,3) null` | |
| `data_completeness_score` | `numeric(5,2) null` | |
| `processing_status` | `varchar(32)` | |
| `is_active` | `boolean` | annonce encore visible/récente |
| `first_seen_at` | `timestamp` | |
| `last_seen_at` | `timestamp` | |
| `created_at` | `timestamp` | |
| `updated_at` | `timestamp` | |

Indexes:

- `uq_licitor_listings_source_url`
- `idx_licitor_listings_auction_datetime`
- `idx_licitor_listings_city`
- `idx_licitor_listings_asset_type`
- `idx_licitor_listings_reserve_price_eur`
- `idx_licitor_listings_processing_status`

## 10.4 Table `licitor_listing_scores`

Rôle:

- stocker le scoring et la stratégie d'enchère
- historiser les recalculs

Champs:

| Champ | Type | Notes |
| --- | --- | --- |
| `id` | `bigint` | PK |
| `listing_id` | `bigint` | FK `licitor_listings.id` |
| `version` | `int` | version du moteur de score |
| `score_total` | `numeric(5,2)` | score final 0-100 |
| `score_data_quality` | `numeric(5,2)` | |
| `score_location` | `numeric(5,2)` | |
| `score_asset_quality` | `numeric(5,2)` | |
| `score_price_gap` | `numeric(5,2)` | |
| `score_liquidity` | `numeric(5,2)` | |
| `score_legal_risk` | `numeric(5,2)` | |
| `score_occupancy_risk` | `numeric(5,2)` | |
| `score_execution_feasibility` | `numeric(5,2)` | visite, délai, contact |
| `predicted_value_low_eur` | `numeric(12,2) null` | |
| `predicted_value_mid_eur` | `numeric(12,2) null` | |
| `predicted_value_high_eur` | `numeric(12,2) null` | |
| `estimated_works_eur` | `numeric(12,2) null` | |
| `estimated_fees_eur` | `numeric(12,2) null` | |
| `target_entry_price_eur` | `numeric(12,2) null` | prix intéressant |
| `max_bid_safe_eur` | `numeric(12,2) null` | plafond prudent |
| `max_bid_aggressive_eur` | `numeric(12,2) null` | plafond offensif |
| `interest_band` | `varchar(32)` | `very_interesting/interesting/speculative/no_go` |
| `recommendation` | `varchar(32)` | `bid/watch/reject/manual_review` |
| `score_inputs_json` | `jsonb` | inputs exacts |
| `score_breakdown_json` | `jsonb` | détails et pénalités |
| `created_at` | `timestamp` | |

Indexes:

- `idx_licitor_listing_scores_listing_id`
- `idx_licitor_listing_scores_score_total`
- `idx_licitor_listing_scores_interest_band`

### 10.5 Pourquoi 4 tables et pas plus

Ce découpage est un bon équilibre:

- `runs` pour l'observabilité
- `snapshots` pour l'audit
- `listings` pour le métier
- `scores` pour l'analyse et les recalculs

Il est inutile en V1 d'ajouter encore:

- une table de contacts séparée
- une table de visite séparée
- une table de features détaillée

Ces données restent en JSONB tant qu'on n'a pas un vrai besoin de requêtage fin.

---

## 11. Règles de normalisation

### 11.1 Type de bien

Le système doit normaliser vers une liste bornée:

- `appartement`
- `studio`
- `maison`
- `immeuble`
- `local_commercial`
- `parking`
- `terrain`
- `autre`

### 11.2 Occupation

Normalisation:

- `vacant`
- `occupied`
- `tenant_in_place`
- `unknown`

### 11.3 Annexes

Stockées en JSONB standardisé:

```json
{
  "cave": true,
  "parking": false,
  "box": false,
  "grenier": false,
  "balcon": null
}
```

### 11.4 Adresse

Séparer:

- `city`
- `district`
- `postal_code`
- `address_line`

Le code postal peut être inféré pour Paris à partir de l'arrondissement, mais doit être marqué comme inféré dans `normalized_json`.

### 11.5 Dates

Toutes les dates sont stockées en ISO / timezone locale claire.

Convention:

- `Europe/Paris`
- conversion en `timestamp without time zone` si la base suit déjà cette convention

---

## 12. Stratégie de scoring

## 12.1 But du scoring

Le scoring doit répondre à quatre questions:

1. l'annonce vaut-elle la peine d'être regardée ?
2. le prix de départ est-il attractif ?
3. jusqu'où peut-on monter aux enchères ?
4. faut-il agir, surveiller, ou rejeter ?

## 12.2 Score final

Proposition simple:

```text
score_total =
  0.10 * score_data_quality +
  0.20 * score_location +
  0.15 * score_asset_quality +
  0.20 * score_price_gap +
  0.10 * score_liquidity +
  0.10 * score_legal_risk +
  0.10 * score_occupancy_risk +
  0.05 * score_execution_feasibility
```

## 12.3 Sous-scores

### `score_data_quality`

Mesure:

- complétude des champs critiques
- confiance extraction
- cohérence déterministe / LLM

### `score_location`

Mesure:

- arrondissement / zone
- attractivité locative
- tension marché

### `score_asset_quality`

Mesure:

- typologie
- surface
- étage
- annexes
- qualité perçue du bien

### `score_price_gap`

Mesure:

- écart entre mise à prix et valeur estimée
- décote nette après frais et travaux

### `score_liquidity`

Mesure:

- revente probable
- facilité de relocation
- profondeur de marché

### `score_legal_risk`

Mesure:

- ambiguïtés annonce
- occupation incertaine
- adresse floue
- mentions problématiques

### `score_occupancy_risk`

Mesure:

- vacant = bonus
- occupé = malus fort
- inconnu = malus modéré

### `score_execution_feasibility`

Mesure:

- visite disponible
- contact exploitable
- annonce suffisamment claire pour agir

---

## 13. Prédiction de prix et stratégie d'enchère

## 13.1 Valeurs cibles à calculer

Le moteur doit calculer:

- `predicted_value_low_eur`
- `predicted_value_mid_eur`
- `predicted_value_high_eur`
- `estimated_works_eur`
- `estimated_fees_eur`
- `target_entry_price_eur`
- `max_bid_safe_eur`
- `max_bid_aggressive_eur`

## 13.2 Définition métier

### `target_entry_price_eur`

Prix où l'annonce devient franchement intéressante.

### `max_bid_safe_eur`

Prix plafond prudent compatible avec:

- marge cible
- frais
- travaux
- buffer risque

### `max_bid_aggressive_eur`

Prix plafond offensif si:

- très forte conviction
- bon marché
- risque faible

## 13.3 Formule simple recommandée

```text
estimated_fees_eur = reserve_price_eur * fee_ratio

target_entry_price_eur =
  (predicted_value_mid_eur - estimated_works_eur - risk_buffer_eur - target_margin_eur)
  / (1 + fee_ratio)

max_bid_safe_eur =
  (predicted_value_low_eur - estimated_works_eur - legal_buffer_eur - safety_margin_eur)
  / (1 + fee_ratio)

max_bid_aggressive_eur =
  (predicted_value_mid_eur - estimated_works_eur - legal_buffer_eur - aggressive_margin_eur)
  / (1 + fee_ratio)
```

## 13.4 Bandes de décision

```text
si reserve_price <= target_entry_price_eur => very_interesting
si reserve_price <= max_bid_safe_eur => interesting
si reserve_price <= max_bid_aggressive_eur => speculative
sinon => no_go
```

## 13.5 Paramètres à configurer

Dans `config.py`:

- `fee_ratio_default`
- `safety_margin_ratio`
- `aggressive_margin_ratio`
- `default_risk_buffer_eur`
- `paris_arrondissement_multipliers`
- `occupancy_discount_map`

---

## 14. API du plugin

Endpoints recommandés:

| Méthode | Route | Rôle |
| --- | --- | --- |
| `POST` | `/api/licitor/runs` | lancer un run |
| `GET` | `/api/licitor/runs` | lister les runs |
| `GET` | `/api/licitor/runs/{id}` | détail d'un run |
| `GET` | `/api/licitor/listings` | lister les annonces canoniques |
| `GET` | `/api/licitor/listings/{id}` | détail annonce |
| `GET` | `/api/licitor/listings/{id}/scores` | scoring et stratégie |
| `POST` | `/api/licitor/listings/{id}/rescore` | recalcul manuel |
| `POST` | `/api/licitor/listings/{id}/refresh` | refetch page détail |

Filtres utiles:

- date d'enchère
- ville / arrondissement
- type de bien
- bande d'intérêt
- occupation
- run_id

---

## 15. Intégration plugin backend

## 15.1 Ajustement du contrat plugin

Le contrat actuel de [backend/app/plugins/base.py](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/plugins/base.py#L20) est trop minimal pour un module opérationnel.

Le plan recommande:

```python
class BusinessModule(ABC):
    name: str
    version: str
    api_prefix: str

    @abstractmethod
    def register_routes(self, app: FastAPI) -> None: ...

    def on_startup(self) -> None: ...

    def register_tasks(self) -> None: ...

    def get_dashboard_kpi(self, db: Session) -> dict: ...
```

## 15.2 Ajustement du bootstrap

Le bootstrap doit cesser d'inclure manuellement les routes plugin dans `main.py` et utiliser réellement [PluginRegistry.load_all](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/plugins/__init__.py#L27).

Objectif:

- `main.py` reste stable
- le plugin Licitor se branche lui-même

## 15.3 Stratégie recommandée

Court terme:

- garder les routes core existantes manuelles
- rendre **au moins Licitor** auto-montable via `PluginRegistry.load_all(app)`

Moyen terme:

- migrer les autres modules vers le même mécanisme

---

## 16. Tâches asynchrones

Tâches Celery minimales:

- `run_licitor_ingestion`
- `rescore_licitor_listing`

Ne pas multiplier les tasks trop tôt.

V1 recommandée:

- un run principal orchestre tout
- rescore séparé seulement pour recalculer la stratégie sans refetch

---

## 17. Observabilité

Le module doit produire:

- métriques run
- top erreurs parsing
- top erreurs LLM
- taux de complétude
- nombre d'annonces scorable / non scorable
- distribution des bandes d'intérêt

Logs structurés recommandés:

- `run_started`
- `list_page_fetched`
- `listing_discovered`
- `detail_fetched`
- `sections_extracted`
- `llm_normalized`
- `listing_upserted`
- `listing_scored`
- `run_completed`

---

## 18. Plan d'implémentation

### Phase 0 — Préparation plugin

1. rendre le chargement plugin réel pour Licitor
2. créer le squelette `backend/app/plugins/licitor/`
3. ajouter config locale et router vide

### Phase 1 — Schéma de données

1. créer les 4 tables plugin
2. créer la migration Alembic
3. brancher les modèles SQLAlchemy

### Phase 2 — Collecte liste + détail

1. fetch page liste
2. teaser parser
3. découverte URLs détail
4. fetch détail
5. stockage HTML en object storage

### Phase 3 — Sectionnement déterministe

1. parser `auction_context`
2. parser `property_summary`
3. parser `occupancy`
4. parser `pricing`
5. parser `location`
6. parser `visit`
7. parser `legal_contact`

### Phase 4 — Structuration LLM

1. écrire le prompt
2. créer le schéma JSON
3. valider via Pydantic
4. gérer fallback et erreurs

### Phase 5 — Normalisation + persistance

1. fusion deterministic + LLM
2. calcul de complétude
3. upsert snapshot
4. upsert canonique

### Phase 6 — Scoring + enchères

1. définir poids et règles
2. calculer sous-scores
3. calculer prix cibles
4. exposer recommandation finale

### Phase 7 — API + lecture produit

1. endpoints runs
2. endpoints listings
3. filtres
4. endpoint rescore

### Phase 8 — Qualité

1. fixtures HTML réelles
2. tests unitaires parser
3. tests contractuels LLM mockés
4. tests d'idempotence
5. tests scoring
6. tests API

---

## 19. Critères d'acceptation

- une page liste Licitor Paris/IDF peut être collectée sans crash
- une annonce standard produit un JSON canonique valide
- les sections clés sont extraites de façon stable
- les runs sont idempotents
- une annonce déjà vue est mise à jour et non dupliquée
- le scoring produit un résultat explicable
- `target_entry_price_eur`, `max_bid_safe_eur` et `max_bid_aggressive_eur` sont calculés
- le plugin peut être monté sans éditer 10 fichiers core

---

## 20. Vérification

### Unit tests

- parser des cartes liste
- parser de sections
- normalisation des arrondissements
- mapping occupation
- calcul scoring
- calcul stratégie enchère

### Integration tests

- run complet sur fixtures HTML
- upsert sans duplication
- persistance snapshot + canonique + score

### API tests

- lancement run
- lecture listings
- filtrage
- rescore

### Observability checks

- métriques run cohérentes
- erreurs LLM visibles
- annonces `needs_review` traçables

---

## 21. Risques et mitigations

| Risque | Impact | Mitigation |
| --- | --- | --- |
| variation HTML Licitor | parsing cassé | sectionnement tolérant + fixtures réelles |
| hallucination LLM | données fausses | JSON strict + evidence + backend validation |
| duplication d'annonces | bruit DB | upsert sur `source_url` unique |
| sur-complexité | dette | 4 tables seulement, pas plus en V1 |
| scoring opaque | perte de confiance | breakdown stocké en JSON + sous-scores lisibles |
| plugin fake | couplage futur | intégrer vrai chargement plugin dès le départ |

---

## 22. Décision finale

La meilleure architecture pour Licitor ici est:

- **plugin backend dédié `licitor`**
- **pipeline simple à 4 couches**: collecte -> sections -> LLM -> scoring
- **4 tables**: runs, snapshots, listings, scores
- **HTML brut hors DB**
- **JSON strict LLM avec evidence**
- **scoring et stratégie d'enchère déterministes**

Cette solution est la plus équilibrée:

- assez simple pour être livrée
- assez propre pour scaler
- assez modulaire pour ne pas redévelopper le module une nouvelle fois à court terme

---

## 23. Fichiers cibles à créer ou modifier

Créations principales:

- `backend/app/plugins/licitor/`
- migration Alembic du plugin
- tests HTML fixtures Licitor
- prompt de normalisation

Évolutions core minimales:

- [backend/app/plugins/base.py](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/plugins/base.py#L20)
- [backend/app/plugins/__init__.py](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/plugins/__init__.py#L19)
- [backend/app/main.py](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/main.py#L63)

---

## 24. Suite logique

Après validation de ce plan, l'ordre recommandé est:

1. finaliser le contrat plugin
2. créer le schéma DB
3. implémenter collecte + sectionnement
4. verrouiller le JSON LLM
5. brancher scoring + stratégie enchère
6. exposer l'API
7. seulement ensuite brancher l'UI
