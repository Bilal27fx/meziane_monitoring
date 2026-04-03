# Refactor Dashboard - 2026-03-25

## Description de la modification

Le dashboard chargeait déjà `/api/dashboard/full`, mais :
- les widgets `OpportunitesWidget` et `LocatairesCards` relançaient des requêtes séparées au lieu d'utiliser les données agrégées du endpoint full ;
- les KPI 3 et 4 affichaient `taux_occupation` et `biens en portefeuille`, alors que la spec dashboard prévoit `alertes actives` et `performance YTD`.

Le refactor corrige ce câblage pour que les sections affichées correspondent au backend et à la documentation d'architecture.

## Fichiers impactés

### d=1 — Appelants / fichiers directement affectés
- `frontend/app/(app)/dashboard/page.tsx`
- `frontend/components/dashboard/OpportunitesWidget.tsx`
- `frontend/components/dashboard/LocatairesCards.tsx`
- `frontend/lib/types/index.ts`

### d=2 — Dépendances indirectes à surveiller
- `frontend/lib/hooks/useDashboard.ts` — conserve les hooks dédiés mais ils ne sont plus utilisés par la page dashboard
- `backend/app/api/dashboard_routes.py` — contrat consommé par le frontend
- `backend/app/schemas/dashboard_schema.py` — source de vérité du shape de réponse

### d=3 — Zones transverses pouvant nécessiter revalidation visuelle
- layout dashboard global
- chargement initial des données dashboard
- cohérence documentaire frontend

## Raison du changement

- Réduire les incohérences entre la spec dashboard et l'écran réel
- Éviter des appels HTTP inutiles pour des données déjà présentes dans `/api/dashboard/full`
- Corriger le mapping des KPI affichés
- Rendre le typage TypeScript cohérent avec les réponses backend réelles

## Tests effectués

- Relecture ciblée du contrat frontend/backend pour :
  - `/api/dashboard/full`
  - `/api/dashboard/locataires`
  - `/api/dashboard/opportunites`
- Vérification des usages directs des composants modifiés via `rg`
- Tentative de `npm run build` dans `frontend/`

## Résultat des tests

Le build frontend n'a pas pu servir de validation finale car l'environnement local est déjà incomplet/incohérent avant ce refactor :
- modules manquants : `@tanstack/react-query`, `react-hot-toast`
- récupération Google Fonts bloquée (`Inter`)

Ces erreurs ne proviennent pas des fichiers modifiés dans ce refactor.

## Impact sur l'architecture

- Le dashboard s'aligne mieux sur l'architecture cible : un endpoint agrégé `/api/dashboard/full` alimente les widgets principaux.
- Les KPI visibles correspondent désormais aux métriques prévues dans la documentation fonctionnelle.
- Le dashboard réduit les appels redondants côté frontend pour les sections Opportunités et Locataires.
