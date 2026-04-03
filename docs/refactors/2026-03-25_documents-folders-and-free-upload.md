# 2026-03-25 — Documents avec dossiers et upload libre

## Besoin produit

Le comportement attendu n'est pas une checklist de types de documents imposés. Le besoin principal est plus simple:

- pouvoir créer un dossier
- nommer ce dossier librement
- uploader ensuite les documents que l'on veut dans ce dossier
- nommer les documents librement
- ne pas forcer des catégories visibles comme `statut`, `kbis`, `piece_identite`, etc.

## Problème actuel

Le module documents actuel est centré sur `type_document` et sur des routes d'upload qui imposent une classification métier. Cette structure est trop rigide pour un usage documentaire simple.

## Direction retenue

Faire évoluer le domaine documents vers un modèle simple `dossier + document`.

## Structure cible

### Entité dossier

Nouvelle table recommandée: `document_folders`

Champs minimum:

- `id`
- `sci_id`
- `bien_id` optionnel
- `locataire_id` optionnel
- `parent_id` optionnel pour permettre des sous-dossiers plus tard
- `nom`
- `created_at`

## Entité document

Faire évoluer `documents` pour qu'un document soit avant tout un fichier stocké et nommé:

- `folder_id` optionnel mais recommandé
- `nom_fichier` reste la vraie source d'affichage
- `type_document` ne doit plus piloter l'UI principale
- `type_document` peut être gardé provisoirement en backend pour compatibilité, mais il doit devenir secondaire ou être réduit à `autre`

## API cible

- `POST /api/documents/folders`
  créer un dossier
- `GET /api/documents/tree`
  récupérer l'arborescence et les documents d'un contexte
- `POST /api/documents/upload`
  uploader un document dans un dossier donné ou à la racine
- `PATCH /api/documents/{id}`
  renommer un document
- `PATCH /api/documents/folders/{id}`
  renommer un dossier
- `DELETE /api/documents/{id}`
  supprimer un document
- `DELETE /api/documents/folders/{id}`
  supprimer un dossier vide ou appliquer une règle claire de cascade

## Règles UX à respecter

- CTA principal: `Uploader un document`
- CTA secondaire: `Créer un dossier`
- aucun libellé métier obligatoire dans l'interface de base
- le nom du document est choisi par l'utilisateur
- le dossier sert de structure visuelle et logique

## Migration conseillée

1. ajouter `document_folders`
2. ajouter `folder_id` sur `documents`
3. garder temporairement `type_document` pour compatibilité technique
4. retirer la checklist et les sélections de type du flux principal
5. basculer les panneaux frontend vers une vue arborescente simple

## Non-objectifs

- GED complexe
- workflow de validation documentaire
- permissions granulaires par dossier
- OCR obligatoire

## Bénéfice

- module plus simple à comprendre
- structure documentaire plus naturelle
- meilleur alignement produit entre backend et usage réel
- moins de dette liée aux taxonomies métier rigides
