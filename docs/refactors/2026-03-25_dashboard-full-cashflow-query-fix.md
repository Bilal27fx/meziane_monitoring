# Refactor Dashboard Full Cashflow Query Fix - 2026-03-25

## Description de la modification

Le endpoint `/api/dashboard/full` plantait dans `get_cashflow_30days()` à cause d'un
`cast(...).type` invalide côté SQLAlchemy/PostgreSQL. Le frontend recevait alors une erreur
sur la requête complète dashboard, puis affichait des valeurs par défaut à `0`.

Le correctif remplace ce groupement par un `GROUP BY Transaction.date` direct, adapté au
type réel de la colonne.

## Fichiers impactés

### d=1 — Appelants / fichiers directement affectés
- `backend/app/services/dashboard_service.py`

### d=2 — Dépendances indirectes à surveiller
- `backend/app/api/dashboard_routes.py`
- `frontend/app/(app)/dashboard/page.tsx`
- `frontend/lib/hooks/useDashboard.ts`

### d=3 — Zones transverses pouvant nécessiter revalidation
- chargement complet du dashboard
- KPI patrimoine
- graphique cashflow 30 jours

## Raison du changement

- Corriger un plantage backend sur `/api/dashboard/full`
- Restaurer la livraison complète des données dashboard
- Éviter l’affichage trompeur de `0` provoqué par une erreur réseau/API

## Tests effectués

- `python -m py_compile backend/app/services/dashboard_service.py`
- exécution directe de `DashboardService.get_full_dashboard()` sur la base locale

## Résultat constaté

Après correction, `get_full_dashboard()` retourne bien :
- `patrimoine_net = 250000.0`
- `cashflow_30days` sur 31 points
- `patrimoine_12months` sur 12 points

## Impact sur l'architecture

- Le endpoint agrégé dashboard redevient exploitable par le frontend.
- Le KPI patrimoine reflète enfin les données réellement présentes en base.
