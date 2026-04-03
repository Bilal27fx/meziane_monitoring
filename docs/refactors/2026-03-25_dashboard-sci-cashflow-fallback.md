# Refactor: dashboard SCI and cashflow fallback

## Description de la modification

- Ajout d'un fallback métier basé sur les baux actifs pour le dashboard.
- `SCI Overview` n'affiche plus `0 €/an` lorsqu'une SCI a des biens loués mais pas encore de transactions de loyer importées.
- Le KPI `Cashflow ce mois` utilise aussi ce fallback mensuel si aucun revenu bancaire positif n'est encore présent sur le mois en cours.

## Fichiers impactés

### d=1 — WILL BREAK / appelants directs

- `backend/app/services/dashboard_service.py`
- `backend/app/api/dashboard_routes.py`
- `frontend/app/(app)/dashboard/page.tsx`
- `frontend/components/dashboard/SCIOverview.tsx`

### d=2 — LIKELY AFFECTED

- `/api/dashboard/kpi`
- `/api/dashboard/full`
- Cartes KPI et bloc `SCI Overview` du dashboard

### d=3 — MAY NEED TESTING

- Cohérence entre cashflow projeté dashboard et transactions bancaires réelles après import
- Cas avec revenus partiellement importés sur certaines SCI

## Raison du changement

- Le dashboard se basait uniquement sur les transactions comptables.
- Une SCI avec bail actif mais sans transaction de loyer encore synchronisée apparaissait donc à `0`, ce qui était faux du point de vue produit.

## Tests effectués

- `python -m py_compile backend/app/services/dashboard_service.py`
- Validation du service via le conteneur backend Docker

## Impact sur l'architecture

- Le dashboard combine maintenant deux sources:
  - transactions réelles quand elles existent
  - projection locative depuis les baux actifs en fallback
- Le contrat API reste inchangé.
