# 2026-03-25 — Formulaire locataire aligné sur le flux documents à deux actions

## Contexte

Le formulaire locataire gardait encore un ancien bloc d'upload direct par zone cliquable, différent du nouveau flux documents du panneau principal. Le besoin était d'appliquer la même logique à tous les uploads documentaires visibles.

## Changements effectués

- remplacement de la zone d'upload directe par deux actions:
  - `Upload document`
  - `Créer un dossier`
- ajout de dossiers en attente côté formulaire avant sauvegarde du locataire
- ajout de documents en attente avec:
  - nom du document
  - dossier cible ou racine
  - fichier sélectionné
- création réelle des dossiers puis upload réel des documents après sauvegarde du locataire

## Fichier impacté

- `frontend/components/admin/forms/LocataireForm.tsx`

## Impact

- d=1 frontend: changement du flux documents dans le formulaire locataire admin
- d=2 métier: meilleure cohérence entre création locataire et bibliothèque documentaire

## Tests effectués

- relecture du composant
- contrôle de portée via recherche de tous les inputs `type="file"` et des hooks documents

## Limite actuelle

La sélection de dossier dans le formulaire locataire s'appuie sur les dossiers racine existants et les dossiers en attente créés dans le formulaire. Si une arborescence complète doit être sélectionnable ici aussi, il faudra exposer une navigation plus riche ou une API d'arbre complète.
