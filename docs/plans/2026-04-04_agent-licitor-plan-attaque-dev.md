# Plan d'attaque — Développement du module Licitor V3 from scratch

**Date :** 2026-04-04  
**Auteur :** Codex  
**Base de référence :** `docs/plans/2026-04-04_agent-licitor-rewrite-complet.md`  
**Statut :** Plan d'exécution technique

---

## But

Ce document décrit **comment développer concrètement** le nouveau module Licitor V3 en repartant de zero sur le moteur interne.

Le principe retenu est:

> **repartir de zero sur le module Licitor, mais conserver l'enveloppe plateforme existante**

On reconstruit:

- l'extraction
- la structuration LLM
- la normalisation
- la qualité
- le scoring input pipeline

On garde:

- les runs
- les events
- l'ingestion globale
- les endpoints
- la persistence générale

---

## Cible d'architecture

### Vue d'ensemble

Le module V3 doit être organisé comme un sous-système lisible, découpé par responsabilité.

```text
backend/app/agents/auction/licitor/
  __init__.py
  models.py
  constants.py
  block_extractor.py
  payload_builder.py
  llm_prompt.py
  structuring_service.py
  normalizer.py
  quality_service.py
  scoring_mapper.py
  orchestrator.py
  fallback_parser.py
```

### Rôle de chaque fichier

| Fichier | Responsabilité |
|---|---|
| `models.py` | Types internes du pipeline |
| `constants.py` | Labels, enums, champs critiques, règles fixes |
| `block_extractor.py` | HTML -> blocs textuels fiables |
| `payload_builder.py` | Construction du payload envoyé au LLM |
| `llm_prompt.py` | Prompt système et contrat de sortie |
| `structuring_service.py` | Appel LLM + validation Pydantic |
| `normalizer.py` | Normalisation métier et fusion des données |
| `quality_service.py` | Complétude, confiance, eligibility |
| `scoring_mapper.py` | Prépare les entrées du scoring backend |
| `fallback_parser.py` | Fallback déterministe minimal si LLM down/invalide |
| `orchestrator.py` | Pipeline complet d'une annonce |

### Intégration avec l'existant

Le module V3 doit être branché ici:

- [licitor.py](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/agents/auction/adapters/licitor.py)
- [auction_ingestion_service.py](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/services/auction_ingestion_service.py)
- [auction_scoring_service.py](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/services/auction_scoring_service.py)
- [auction_listing.py](/Users/bilalmeziane/Desktop/Meziane_Monitoring/backend/app/models/auction_listing.py)

L'adapter historique devient une **façade mince** qui délègue au nouvel orchestrateur.

---

## Architecture logique

### 1. Couche extraction

Entrée:

- HTML audience
- HTML détail
- URL source

Sortie:

- blocs textuels
- liens documents
- texte complet
- contexte session disponible

Cette couche ne décide pas du sens métier profond.

### 2. Couche structuration

Entrée:

- blocs extraits
- contexte session
- URL

Sortie:

- JSON structuré strict
- preuves textuelles
- score de confiance brut

Cette couche repose sur le LLM.

### 3. Couche normalisation

Entrée:

- extraction déterministe
- JSON structuré LLM

Sortie:

- objet métier canonique
- flags `explicit/inferred/unknown`
- résolution des conflits

### 4. Couche qualité

Entrée:

- objet canonique
- preuves
- état du pipeline

Sortie:

- complétude
- champs critiques manquants
- eligibility scoring
- statut qualité

### 5. Couche scoring bridge

Entrée:

- objet canonique validé

Sortie:

- payload propre pour `auction_scoring_service`
- breakdown des données utilisées

---

## Modèles internes à créer

### `ExtractedBlock`

```python
class ExtractedBlock(BaseModel):
    name: str
    text: str | None
    source: str
    confidence: float = 1.0
```

### `LicitorExtractedBlocks`

```python
class LicitorExtractedBlocks(BaseModel):
    source_url: str
    header_text: str | None = None
    title_text: str | None = None
    description_text: str | None = None
    price_text: str | None = None
    address_text: str | None = None
    occupancy_text: str | None = None
    visit_text: str | None = None
    cadastre_text: str | None = None
    document_urls: list[str] = []
    full_text: str
```

### `LicitorStructuredData`

```python
class LicitorStructuredData(BaseModel):
    property_type: str | None = None
    city: str | None = None
    postal_code: str | None = None
    postal_code_inferred: bool = False
    address: str | None = None
    reserve_price: float | None = None
    surface_m2: float | None = None
    bedrooms: int | None = None
    rooms_total: int | None = None
    rooms_total_inferred: bool = False
    floor: int | None = None
    floor_label: str | None = None
    has_cave: bool | None = None
    has_parking: bool | None = None
    occupancy_status: str | None = None
    auction_date: datetime | None = None
    auction_tribunal: str | None = None
    visit_start: datetime | None = None
    visit_end: datetime | None = None
    risks: list[str] = []
    category_labels: list[str] = []
    confidence: float = 0.0
    evidence: dict[str, str] = {}
```

### `LicitorCanonicalListing`

```python
class LicitorCanonicalListing(BaseModel):
    listing_type: str | None = None
    title: str | None = None
    city: str | None = None
    postal_code: str | None = None
    address: str | None = None
    reserve_price: float | None = None
    surface_m2: float | None = None
    nb_pieces: int | None = None
    nb_chambres: int | None = None
    etage: int | None = None
    type_etage: str | None = None
    cave: bool | None = None
    parking: bool | None = None
    occupancy_status: str | None = None
    visit_dates: list[str] = []
    property_details: dict = {}
    quality_flags: dict = {}
    extraction_trace: dict = {}
    structured_data: dict = {}
```

---

## Contrat de module

### API publique minimale du nouveau module

Le coeur V3 doit exposer:

```python
class LicitorPipelineOrchestrator:
    def process_listing_detail(
        self,
        *,
        detail_html: str,
        page_url: str,
        session_context: dict,
        listing_preview: dict | None = None,
    ) -> LicitorCanonicalListing:
        ...
```

### Contrat d'adaptation pour l'ancien adapter

L'ancien adapter continuera à exposer:

- `parse_sessions`
- `parse_listing_cards`
- `parse_listing_detail`

Mais `parse_listing_detail` deviendra un simple pont entre l'interface historique et l'orchestrateur V3.

---

## Plan d'attaque par phases

## Phase 0 — Gel du contrat

### Objectif

Ne pas coder sans schéma définitif.

### Travaux

1. figer les modèles Pydantic internes
2. figer le JSON de sortie du LLM
3. figer les champs DB à ajouter
4. figer la liste des champs critiques
5. figer les états du pipeline

### Definition of done

- `models.py` validé
- `constants.py` validé
- schéma JSON V1 documenté

### Risque si on saute cette phase

Réécriture du prompt, de la DB et des tests en boucle.

---

## Phase 1 — Fixtures réelles

### Objectif

Construire le dataset réel avant le moteur.

### Travaux

1. créer `backend/tests/fixtures/licitor/`
2. ajouter des pages audience et détail réelles
3. créer un fichier manifest JSON attendu
4. couvrir les cas edge prioritaires

### Cas à couvrir

- appartement Paris avec arrondissement
- bien loué
- visite sans adresse parfaite
- cave condamnée
- parking seul
- surface manquante
- occupation ambiguë
- page avec plusieurs lignes descriptives
- page avec cadastre massif

### Definition of done

- au moins 15 cas réels exploitables
- chaque fixture a un expected JSON minimal

---

## Phase 2 — Block extractor

### Objectif

Obtenir une extraction stable et simple à déboguer.

### Travaux

1. parser le HTML avec BeautifulSoup
2. isoler les zones fortes du contenu
3. extraire les blocs métier
4. remonter les documents et liens
5. produire `LicitorExtractedBlocks`

### Règles de design

- pas de logique de score
- pas de logique métier profonde
- pas d'inférence lourde

### Tests

- un test par bloc
- un test page complète -> tous blocs

### Definition of done

- extraction stable sur le dataset fixture
- pas de crash sur HTML incomplet

---

## Phase 3 — Prompt et structuration LLM

### Objectif

Transformer les blocs en JSON métier strict.

### Travaux

1. écrire `llm_prompt.py`
2. écrire le modèle Pydantic de sortie
3. brancher le client LLM
4. gérer le parse JSON
5. gérer les erreurs et timeouts

### Règles prompt

- sortie JSON uniquement
- `null` si inconnu
- pas d'invention
- preuves obligatoires
- `*_inferred=true` si déduit

### Tests

- validation du schéma
- test de refus des JSON invalides
- test des preuves obligatoires

### Definition of done

- 100% des réponses valides passent par Pydantic
- les réponses invalides tombent en fallback propre

---

## Phase 4 — Fallback parser

### Objectif

Garantir que le pipeline survit sans LLM.

### Travaux

1. extraire un minimum déterministe
2. remplir prix, ville, date, occupation si possible
3. marquer les champs faibles
4. produire un objet canonique dégradé

### Cas d'usage

- LLM indisponible
- JSON invalide
- timeout
- quota dépassé

### Definition of done

- une annonce persistable même sans structuration LLM

---

## Phase 5 — Normalizer

### Objectif

Transformer la structuration en données canoniques cohérentes.

### Travaux

1. normaliser les villes
2. normaliser les arrondissements
3. déduire certains codes postaux avec flag
4. harmoniser les labels de type de bien
5. harmoniser l'occupation
6. fusionner extraction forte et structuration LLM

### Règle d'arbitrage

- déterministe explicite > LLM
- LLM > heuristique faible

### Definition of done

- sortie `LicitorCanonicalListing` stable

---

## Phase 6 — Quality service

### Objectif

Décider si l'annonce est exploitable.

### Travaux

1. calculer `completeness_score`
2. calculer `critical_missing_fields`
3. calculer `scoring_eligibility`
4. calculer `final_confidence`
5. classer `high/medium/low`

### Definition of done

- chaque annonce a un statut qualité intelligible

---

## Phase 7 — Scoring mapper

### Objectif

Préparer une entrée propre pour le scoring backend.

### Travaux

1. mapper l'objet canonique vers `AuctionListing`
2. produire un snapshot `scoring_inputs`
3. exposer les preuves utiles au score
4. distinguer score complet et score dégradé

### Definition of done

- le scoring backend n'a plus besoin de relire le texte brut

---

## Phase 8 — Orchestrator

### Objectif

Assembler toutes les briques dans un pipeline unique.

### Séquence

1. `extract_blocks`
2. `build_payload`
3. `structure_with_llm`
4. `fallback_if_needed`
5. `normalize`
6. `assess_quality`
7. `map_for_scoring`
8. `return canonical listing`

### Definition of done

- une seule entrée
- une seule sortie canonique
- logs par étape

---

## Phase 9 — Intégration plateforme

### Objectif

Brancher V3 dans le produit sans casser les runs existants.

### Travaux

1. faire de `adapters/licitor.py` une façade
2. mettre à jour `auction_ingestion_service.py`
3. ajouter les colonnes DB
4. stocker `structured_data`, `quality_flags`, `extraction_trace`
5. adapter les réponses API si utile

### Definition of done

- run complet fonctionnel via l'API existante

---

## Phase 10 — Vérification complète

### Objectif

Valider le module avant usage réel.

### Travaux

1. tests unitaires
2. tests intégration
3. tests de non-régression sur fixtures
4. audit des taux de complétude
5. audit des causes de fallback

### KPIs de sortie

- >95% prix
- >95% date audience
- >95% ville ou code postal
- >90% occupation
- 0 crash run sur fixtures

---

## Ordre de création des fichiers

Créer dans cet ordre:

1. `models.py`
2. `constants.py`
3. `block_extractor.py`
4. `llm_prompt.py`
5. `structuring_service.py`
6. `fallback_parser.py`
7. `normalizer.py`
8. `quality_service.py`
9. `scoring_mapper.py`
10. `orchestrator.py`

Ensuite seulement:

11. adaptation de `adapters/licitor.py`
12. adaptation de `auction_ingestion_service.py`
13. migration DB
14. adaptation des tests d'intégration

---

## Stratégie de branches de développement

### Découpage recommandé

1. `feat/licitor-v3-contracts`
2. `feat/licitor-v3-fixtures`
3. `feat/licitor-v3-extractor`
4. `feat/licitor-v3-structuring`
5. `feat/licitor-v3-normalization-quality`
6. `feat/licitor-v3-scoring-bridge`
7. `feat/licitor-v3-integration`

### Pourquoi

Ça évite un énorme diff opaque et permet de valider chaque couche.

---

## Checklist de démarrage

Avant d'écrire la première ligne de code:

- valider le schéma JSON LLM
- valider les champs DB à ajouter
- valider les fixtures prioritaires
- valider les catégories métier minimales
- valider les champs critiques pour le score

---

## Checklist de review technique

Avant de fusionner la V1:

- le module n'a qu'une responsabilité par fichier
- aucun regex spaghetti central de 800 lignes
- le LLM ne reçoit pas du HTML brut
- le scoring ne dépend pas directement du texte brut
- chaque champ critique a une preuve ou un flag d'inférence
- le fallback fonctionne sans casser le run
- les métriques de qualité sont persistées

---

## Résultat attendu

À la fin de ce plan d'attaque, on doit avoir un module Licitor V3 qui:

- est lisible
- est découpé
- est testable
- supporte les pages réelles
- produit un JSON structuré propre
- rend le scoring stable

Et surtout:

> on ne reviendra plus corriger l'agent en empilant des regex dans un seul adapter monolithique.

