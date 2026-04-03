# 2026-03-25 — Mutualisation du flux documentaire à deux actions

## Contexte

Le panneau documents et le formulaire locataire utilisaient déjà le même comportement produit, mais avec deux implémentations frontend séparées. Cette duplication créait une dette immédiate: toute évolution UX risquait de diverger entre les deux écrans.

## Changement

- création du composant partagé `frontend/components/admin/documents/DocumentActionComposer.tsx`
- extraction de la logique UI commune:
  - `Upload document`
  - `Créer un dossier`
  - saisie différée après clic
  - choix du dossier cible
  - sélection du fichier
- rebranchement de:
  - `frontend/components/admin/panels/DocumentsPanel.tsx`
  - `frontend/components/admin/forms/LocataireForm.tsx`

## Impact

- d=1 frontend: mutualisation du flux documentaire sur les écrans admin actifs
- d=2 architecture: réduction du couplage et meilleur point d'entrée pour faire évoluer l'UX documents

## Bénéfice architecture

- une seule source de vérité pour l'interaction documentaire
- maintenance plus simple
- évolution plus fluide si l'on ajoute ensuite:
  - validation
  - support de plusieurs fichiers
  - arbre complet de dossiers
  - instrumentation analytics

## Vérifications

- contrôle manuel des appelants de `DocumentsPanel` et `LocataireForm`
- relecture de la portée après extraction

## Limite actuelle

Le composant partagé mutualise le flux d'action, mais la résolution des dossiers et la persistance restent pilotées par chaque parent, ce qui est volontaire pour garder des responsabilités claires.
