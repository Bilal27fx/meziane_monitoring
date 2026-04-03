# 2026-03-25 — Fondation bibliothèque documents avec dossiers

## Contexte

Le module documents était piloté par `type_document` et imposait des catégories métier visibles dans l'interface. Le besoin produit était plus simple: créer un dossier, le nommer, puis uploader librement des documents nommés par l'utilisateur.

## Changement

- ajout du modèle `document_folders`
- ajout de `folder_id` sur `documents`
- ajout d'une API bibliothèque `/api/documents/library`
- ajout d'une API de création de dossier `/api/documents/folders`
- upload libre dans un dossier ou à la racine avec `nom_document`
- bascule du panneau admin documents vers `Créer un dossier` et `Uploader un document`
- suppression des catégories visibles dans le flux principal d'upload

## Impact

- backend: nouveau découpage documentaire plus proche du besoin produit
- base de données: migration Alembic requise
- frontend: panneau documents réorienté vers une logique dossier/fichier
- compatibilité: `type_document` est conservé provisoirement en backend avec la valeur `autre`
