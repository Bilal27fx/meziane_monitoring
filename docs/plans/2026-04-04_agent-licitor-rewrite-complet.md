# Plan — Refonte complète de l'agent Licitor

**Date :** 2026-04-04  
**Auteur :** Codex  
**Statut :** Proposition détaillée avant exécution

---

## Contexte

L'agent Licitor actuel fonctionne, mais son coeur est trop couplé:

- le parsing HTML mélange extraction, normalisation métier et heuristiques
- le scoring dépend encore trop de champs partiellement extraits
- les corrections se font par accumulation de regex dans un seul fichier
- il est difficile de savoir pourquoi un champ a été extrait, inféré, ou raté

Le besoin exprimé ici est plus radical qu'un correctif incrémental:

1. **refaire complètement l'agent**
2. **extraire les données utiles de manière fiable**
3. **envoyer un payload propre au LLM**
4. **laisser le LLM produire un JSON structuré de catégorisation**
5. **calculer le scoring à partir de ce JSON**
6. **rendre le pipeline testable, observable et stable**

L'idée centrale retenue est donc:

> **HTML -> extraction déterministe minimale -> structuration/catégorisation LLM -> validation stricte -> scoring déterministe -> persistance**

---

## Décision d'architecture

La refonte est **complète sur le moteur Licitor**, mais **pas destructive pour la plateforme**.

On conserve les briques déjà utiles autour:

- les `AgentRun` / `AgentRunEvent`
- les endpoints de lancement
- l'ingestion idempotente vers la base
- le modèle `AuctionListing`
- la mécanique de fetch HTTP / Celery

En revanche, on **remplace intégralement la logique interne de l'agent Licitor** par un pipeline clair à étapes séparées.

Autrement dit:

- **on ne patch plus le parser actuel**
- **on reconstruit un moteur Licitor V3**
- **on garde l'enveloppe système existante pour éviter une régression produit inutile**

---

## Objectifs produit

Le nouvel agent doit permettre:

1. d'ingérer une audience Licitor complète sans crash
2. de produire un JSON structuré homogène pour chaque annonce
3. de distinguer clairement les données **extraites**, **inférées** et **inconnues**
4. de calculer un score explicable pour chaque annonce scorable
5. de suivre le taux de complétude, les échecs LLM et les causes de non-score

---

## Non-objectifs

Ce plan ne vise pas à:

- créer un agent générique multi-sources dès la V1
- laisser le LLM consommer le HTML brut directement
- faire du scoring opaque entièrement piloté par LLM
- introduire de nouvelles dépendances lourdes sans nécessité

---

## Principes de conception

### 1. Extraction minimale, fiable, bornée

Le scraper ne doit pas "comprendre" toute l'annonce.  
Son rôle est de récupérer des **blocs de texte fiables**.

### 2. Le LLM structure, il ne remplace pas la collecte

Le LLM reçoit un payload textuel propre et retourne un JSON strict validé par schéma.

### 3. Le backend garde la décision métier finale

Le LLM aide à:

- structurer
- catégoriser
- identifier des risques
- ajouter une confiance

Mais le **score final** reste calculé côté backend.

### 4. Toute donnée importante doit avoir une trace

Pour chaque champ important, on doit pouvoir retrouver:

- la valeur
- son niveau de confiance
- sa source textuelle
- si elle a été inférée ou explicitement lue

---

## Architecture cible

### Pipeline cible

1. `fetch`
2. `extract_blocks`
3. `build_structuring_payload`
4. `llm_structuring`
5. `validate_structured_json`
6. `normalize_and_merge`
7. `quality_assessment`
8. `score_listing`
9. `persist`
10. `notify/report`

### Flux détaillé

#### Étape 1 — Fetch

Récupération de:

- la page audience
- les pages paginées
- les pages détail

Le fetch reste piloté par le service existant, mais avec logs plus précis:

- audience fetchée
- nombre de pages audience découvertes
- nombre de pages détail fetchées
- erreurs HTTP par URL

#### Étape 2 — Extraction de blocs

Le nouvel agent Licitor ne sort pas directement un `AuctionListing` final.  
Il produit d'abord des blocs comme:

- `header_text`
- `title_text`
- `description_text`
- `price_text`
- `address_text`
- `occupancy_text`
- `visit_text`
- `cadastre_text`
- `documents`
- `full_text`

#### Étape 3 — Payload LLM

Le payload envoyé au LLM doit être stable, compact et lisible.

Exemple:

```json
{
  "source": "licitor",
  "source_url": "https://www.licitor.com/annonce/...",
  "session_context": {
    "tribunal": "Tribunal Judiciaire de Paris",
    "auction_date_text": "jeudi 9 avril 2026 à 14h"
  },
  "listing_blocks": {
    "title_text": "UN APPARTEMENT",
    "description_text": "au 24ème étage, avec : dégagement, salon, deux chambres...",
    "price_text": "Mise à prix : 100 000 €",
    "address_text": "Paris 13ème / 130, bd Massena",
    "occupancy_text": "Les lieux sont loués",
    "visit_text": "Visite sur place jeudi 26 mars 2026 de 12h à 13h",
    "cadastre_text": "Cadastrés : dans les lots de volume...",
    "full_text": "..."
  }
}
```

#### Étape 4 — Structuration LLM

Le LLM doit produire un JSON strict contenant:

- les champs immobiliers utiles
- les catégories
- les risques
- la confiance
- les preuves textuelles

#### Étape 5 — Validation stricte

Le JSON LLM est validé par Pydantic.

Si le JSON est invalide:

- on loggue l'erreur
- on marque l'annonce `structured_failed`
- on tente un fallback déterministe minimal

#### Étape 6 — Normalisation / merge

On fusionne:

- les champs déterministes extraits directement
- les champs structurés par LLM
- les règles métier de normalisation locale

Exemple:

- `Paris 13ème` -> `city = Paris 13eme`
- `postal_code = 75013` si inféré à partir de l'arrondissement
- `deux chambres` -> `bedrooms = 2`
- `salon + deux chambres` -> `rooms_total = 3` avec `is_inferred = true`

#### Étape 7 — Qualité / confiance

On calcule:

- `extraction_completeness`
- `critical_missing_fields`
- `structured_confidence`
- `final_confidence`
- `scoring_eligibility`

#### Étape 8 — Scoring

Le scoring utilise le JSON structuré validé, pas le texte brut.

#### Étape 9 — Persistance

On persiste:

- les champs canoniques
- le JSON structuré
- la trace d'extraction
- les preuves
- le score

#### Étape 10 — Reporting

On expose:

- nombre d'annonces extraites
- nombre structurées
- nombre scorées
- taux de complétude
- top champs manquants
- top causes de rejet

---

## Contrat de données cible

### 1. Bloc brut extrait

Créer un objet interne du type:

```json
{
  "field": "occupancy_text",
  "value": "Les lieux sont loués",
  "source_block": "occupancy",
  "confidence": 0.95,
  "is_inferred": false
}
```

### 2. JSON structuré attendu du LLM

Le LLM doit produire un JSON du type:

```json
{
  "property_type": "appartement",
  "city": "Paris 13eme",
  "postal_code": "75013",
  "postal_code_inferred": true,
  "address": "130 bd Massena",
  "reserve_price": 100000,
  "surface_m2": null,
  "bedrooms": 2,
  "rooms_total": 3,
  "rooms_total_inferred": true,
  "floor": 24,
  "floor_label": "etage",
  "has_cave": true,
  "cave_notes": ["cave condamnee"],
  "has_parking": true,
  "occupancy_status": "loue",
  "auction_date": "2026-04-09T14:00:00",
  "auction_tribunal": "TJ Paris",
  "visit_start": "2026-03-26T12:00:00",
  "visit_end": "2026-03-26T13:00:00",
  "risks": [
    "cave_condamnee",
    "surface_non_trouvee"
  ],
  "category_labels": [
    "appartement",
    "paris_intramuros",
    "occupe_ou_loue"
  ],
  "confidence": 0.86,
  "evidence": {
    "bedrooms": "deux chambres",
    "occupancy_status": "Les lieux sont loués",
    "price": "Mise à prix : 100 000 €",
    "visit": "Visite sur place jeudi 26 mars 2026 de 12h à 13h"
  }
}
```

### 3. Modèle canonique persisté

Le modèle final en base doit contenir:

- champs principaux de `AuctionListing`
- `structured_data_json`
- `extraction_trace_json`
- `quality_flags_json`
- `scoring_inputs_json`

---

## Répartition des responsabilités

### Ce que fait l'extraction déterministe

- récupérer les URLs
- découper les blocs de texte
- extraire les documents / liens
- extraire quelques champs certains à très forte confiance
- préserver le texte brut utile

### Ce que fait le LLM

- structurer le texte en JSON homogène
- convertir les nombres écrits
- catégoriser les types de bien
- normaliser l'occupation
- repérer les signaux de risque
- fournir des preuves textuelles

### Ce que fait le backend métier

- valider le JSON
- normaliser les valeurs
- rejeter les valeurs incohérentes
- calculer les scores
- décider si l'annonce est scorable

---

## Scoring cible

Le scoring doit devenir **100% explicable**.

### Score V1 recommandé

| Axe | Pondération |
|---|---|
| Prix / décote apparente | 35 |
| Localisation | 20 |
| Occupation | 15 |
| Liquidité | 10 |
| Qualité intrinsèque du bien | 10 |
| Risques / anomalies | 10 |

### Données d'entrée minimales pour scorer

Une annonce est `scorable` si on a au minimum:

- `reserve_price`
- `city` ou `postal_code`
- `property_type`
- `occupancy_status`
- `auction_date`

`surface_m2` améliore fortement le score mais ne doit pas toujours bloquer la création d'un score dégradé.

### Types de sortie de score

- `score_global`
- `score_breakdown`
- `recommandation`
- `motifs`
- `blocking_risks`

### Règle critique

Le LLM peut proposer des `risks` et des `category_labels`, mais **ne calcule pas seul le score final**.

---

## Observabilité et qualité

### Métriques à suivre

- taux de fetch réussi par audience
- taux de pages détail parsées
- taux de structuration LLM réussie
- taux de JSON invalides
- taux d'annonces scorables
- taux d'annonces scorées
- top 10 champs manquants
- top 10 causes de fallback
- coût LLM par run

### Indicateurs par annonce

- `raw_extraction_ok`
- `llm_structuring_ok`
- `structured_confidence`
- `critical_missing_fields`
- `scoring_eligibility`
- `score_status`

### Journalisation

Chaque run doit pouvoir répondre à:

- combien d'annonces ont été récupérées
- combien sont passées en structuration LLM
- combien ont échoué au parsing
- combien ont échoué à la validation JSON
- combien ont été scorées
- pourquoi les autres ne l'ont pas été

---

## Design du prompt LLM

### Rôle du prompt système

Le prompt système doit imposer:

- aucune invention
- retour JSON strict
- `null` si l'information n'est pas présente
- preuve textuelle pour chaque champ important
- distinction entre `explicit` et `inferred`

### Règles de sortie

- ne jamais remplir une valeur sans preuve ou inférence raisonnable
- ne jamais convertir un arrondissement en code postal sans marquer `postal_code_inferred = true`
- ne jamais supposer une surface
- signaler les incohérences dans `risks`

### Gestion de la température

Utiliser une température faible pour réduire la variance.

---

## Stratégie de fallback

Si le LLM échoue:

1. on garde les blocs bruts
2. on applique un petit normaliseur déterministe minimal
3. on persiste l'annonce
4. on marque `llm_structuring_ok = false`
5. on laisse l'annonce non scorée ou scorée en mode dégradé

Ce fallback est obligatoire pour ne pas bloquer tout le run sur une erreur LLM.

---

## Organisation technique proposée

### Fichiers à créer

| Fichier | Rôle |
|---|---|
| `backend/app/agents/auction/licitor/block_extractor.py` | Découpage HTML -> blocs textuels |
| `backend/app/agents/auction/licitor/models.py` | Modèles internes d'extraction / structuration |
| `backend/app/agents/auction/licitor/structuring_service.py` | Appel LLM + validation du JSON |
| `backend/app/agents/auction/licitor/normalizer.py` | Normalisation métier locale |
| `backend/app/agents/auction/licitor/quality_service.py` | Calcul complétude / confiance |
| `backend/app/agents/auction/licitor/orchestrator.py` | Pipeline complet pour une audience / annonce |
| `backend/tests/fixtures/licitor/*.html` | Jeux de pages réelles anonymisées |
| `backend/tests/services/test_licitor_structuring_service.py` | Tests de validation JSON LLM |
| `backend/tests/integration/test_licitor_pipeline_end_to_end.py` | Tests bout-en-bout |

### Fichiers à refondre ou adapter

| Fichier | Action |
|---|---|
| `backend/app/agents/auction/adapters/licitor.py` | Remplacement par adaptateur mince branché sur le nouveau moteur |
| `backend/app/services/auction_ingestion_service.py` | Brancher le pipeline structuration + qualité + scoring |
| `backend/app/services/auction_scoring_service.py` | Recentrer sur le scoring déterministe depuis JSON structuré |
| `backend/app/models/auction_listing.py` | Ajouter colonnes JSON de trace / structuration / qualité |
| `backend/app/schemas/auction_schema.py` | Exposer les nouveaux champs utiles si nécessaires |
| `backend/tests/services/test_auction_ingestion_service.py` | Adapter aux nouveaux états et métriques |

### Colonnes DB à ajouter

| Colonne | Type | Rôle |
|---|---|---|
| `structured_data` | JSON | JSON structuré validé du LLM |
| `extraction_trace` | JSON | Preuves et sources textuelles |
| `quality_flags` | JSON | Champs manquants, confiance, eligibilité |
| `scoring_inputs` | JSON | Snapshot des données utilisées pour scorer |
| `structuring_status` | String | `pending/success/failed/fallback` |
| `structured_at` | DateTime | Date de structuration |

---

## Plan d'exécution détaillé

### Phase 0 — Cadrage et gel du contrat

**Objectif :** éviter de coder sans cible stable.

Travaux:

1. définir le JSON cible du LLM
2. définir les champs DB à persister
3. définir les champs critiques pour le scoring
4. figer les catégories métier
5. choisir les statuts du pipeline

Livrables:

- schéma JSON structuré V1
- liste des colonnes DB
- liste des métriques de qualité

### Phase 1 — Dataset de référence

**Objectif :** arrêter de tester sur des snippets trop simples.

Travaux:

1. collecter 15 à 30 pages Licitor réelles
2. les anonymiser si nécessaire
3. créer un dossier de fixtures versionné
4. écrire un expected JSON pour chaque cas important

Cas obligatoires:

- appartement Paris avec arrondissement sans code postal explicite
- bien loué / occupé
- cave condamnée
- parking / box / cave multiples
- adresse sur plusieurs lignes
- visite avec plage horaire
- occupation ambiguë
- surface absente
- lots / cadastre volumineux

Livrables:

- fixtures HTML
- fixtures JSON attendues

### Phase 2 — Nouveau moteur d'extraction de blocs

**Objectif :** remplacer le parsing ad hoc.

Travaux:

1. implémenter `block_extractor.py`
2. détecter les zones principales du DOM
3. produire un objet `ExtractedBlocks`
4. conserver le texte brut complet

Sortie attendue:

- extraction stable même si la normalisation échoue ensuite

### Phase 3 — Structuration LLM

**Objectif :** produire un JSON homogène et validé.

Travaux:

1. écrire le prompt système
2. écrire le modèle Pydantic de réponse
3. brancher l'appel LLM
4. gérer erreurs, timeouts, JSON invalides
5. stocker les preuves et la confiance

Sortie attendue:

- `structured_data` valide ou fallback propre

### Phase 4 — Normalisation métier

**Objectif :** fiabiliser les champs avant scoring.

Travaux:

1. normaliser villes / arrondissements / codes postaux
2. normaliser types de bien
3. normaliser occupation
4. dédupliquer catégories et risques
5. arbitrer en cas de conflit extraction déterministe / LLM

Règle d'arbitrage:

- prioriser le déterministe sur le LLM quand la preuve est explicite
- prioriser le LLM sur des inférences lexicales complexes

### Phase 5 — Qualité et eligibilité

**Objectif :** savoir si l'annonce est exploitable.

Travaux:

1. calculer `critical_missing_fields`
2. calculer `completeness_score`
3. calculer `scoring_eligibility`
4. classer les annonces en `high/medium/low confidence`

### Phase 6 — Scoring V1

**Objectif :** rendre le scoring stable et explicable.

Travaux:

1. redéfinir les entrées minimales du scoring
2. calculer les sous-scores
3. stocker le breakdown complet
4. produire une recommandation métier

### Phase 7 — Intégration orchestration

**Objectif :** brancher le nouveau moteur au pipeline existant.

Travaux:

1. intégrer dans le run d'ingestion
2. enrichir les logs de run
3. enrichir les compteurs exposés au frontend
4. garantir l'idempotence

### Phase 8 — Tests et durcissement

**Objectif :** valider sur cas réels avant mise en prod.

Travaux:

1. tests unitaires de blocs
2. tests de validation JSON
3. tests d'intégration
4. tests de non-régression sur fixtures
5. mesure des taux d'extraction et de scoring

---

## Stratégie de tests

### Niveau 1 — Unit

Tester:

- extraction des blocs
- validation Pydantic du JSON LLM
- normalisation des villes / occupation / types

### Niveau 2 — Adapter

Tester:

- page détail réelle -> `ExtractedBlocks`
- `ExtractedBlocks` -> `structured_data`

### Niveau 3 — Integration

Tester:

- audience -> listings -> structuration -> scoring -> DB

### Niveau 4 — Regression dataset

Pour chaque fixture réelle:

- comparer JSON attendu vs JSON produit
- mesurer les champs critiques ratés
- suivre l'évolution après chaque changement

---

## Critères d'acceptation

Le rewrite est considéré comme réussi si:

1. aucune page fixture ne fait planter le run
2. `reserve_price` est extrait ou structuré sur plus de 95% des cas du dataset
3. `auction_date` est extrait ou structuré sur plus de 95% des cas
4. `city/postal_code` est disponible sur plus de 95% des cas
5. `occupancy_status` est disponible sur plus de 90% des cas
6. 100% des annonces avec données minimales sont scorées ou explicitement marquées non scorables
7. chaque score possède un breakdown et des raisons
8. chaque champ clé possède une preuve textuelle ou un flag d'inférence

---

## Risques et points de vigilance

### Risque 1 — LLM trop permissif

Mitigation:

- schéma strict
- température faible
- preuves obligatoires
- fallback déterministe

### Risque 2 — HTML réel hétérogène

Mitigation:

- dataset réel de fixtures
- bloc extractor robuste
- éviter les regex globales trop fragiles

### Risque 3 — Explosion des cas edge

Mitigation:

- extraire des blocs génériques
- laisser le LLM faire la structuration sémantique
- versionner les catégories métier

### Risque 4 — Score peu fiable si données partielles

Mitigation:

- notion d'eligibilité
- score dégradé distinct
- flags de confiance visibles

---

## Ordre recommandé d'implémentation

1. schéma JSON cible
2. fixtures HTML réelles
3. nouveaux modèles internes
4. block extractor
5. service de structuration LLM
6. normalizer
7. quality service
8. scoring V1
9. branchement ingestion
10. tests de régression

---

## Recommandation finale

La bonne approche n'est pas:

- ni de continuer à empiler des regex dans l'adapter actuel
- ni de faire `HTML brut -> score LLM direct`

La bonne approche pour ce projet est:

> **refaire complètement l'agent autour d'un pipeline extraction minimale + JSON LLM structuré + scoring backend explicable**

Ce design est plus simple à faire évoluer, plus stable sur les cas réels, et bien plus facile à tester que l'agent actuel.

---

## Livrable attendu après exécution de ce plan

À la fin du chantier, l'agent Licitor doit être capable de prendre une annonce comme:

```text
Tribunal Judiciaire de Paris
Vente aux enchères publiques
jeudi 9 avril 2026 à 14h
UN APPARTEMENT
au 24ème étage, avec :
dégagement, salon, deux chambres, salle de bains, wc, cuisine, placards
Une cave
au 3ème étage sous-sol
D'après les éléments recueillis lors des opérations de description, la cave aurait été condamnée
Un emplacement de parking
bâtiment A8 "Ravenne", au 3ème étage sous-sol

Les lieux sont loués
Mise à prix : 100 000 €
Paris 13ème
130, bd Massena
Visite sur place jeudi 26 mars 2026 de 12h à 13h
```

et d'en sortir:

- un `AuctionListing` cohérent
- un JSON structuré validé
- une trace d'extraction avec preuves
- une décision de scoring explicable
- un état de qualité clair

