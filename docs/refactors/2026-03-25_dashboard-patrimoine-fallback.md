# Refactor Dashboard Patrimoine Fallback - 2026-03-25

## Description de la modification

Le dashboard calculait la valorisation patrimoine uniquement à partir de `bien.valeur_actuelle`.
Quand ce champ était vide mais que `prix_acquisition` était renseigné, plusieurs zones du dashboard
pouvaient retomber à `0` ou rester vides.

Le refactor ajoute un fallback `coalesce(valeur_actuelle, prix_acquisition)` dans les calculs
de valorisation utilisés par le dashboard.

## Fichiers impactés

### d=1 — Appelants / fichiers directement affectés
- `backend/app/services/dashboard_service.py`

### d=2 — Dépendances indirectes à surveiller
- `backend/app/api/dashboard_routes.py`
- `frontend/app/(app)/dashboard/page.tsx`
- `frontend/components/dashboard/SCIOverview.tsx`
- `frontend/components/dashboard/Top5Biens.tsx`

### d=3 — Zones transverses pouvant nécessiter revalidation
- KPI `Patrimoine net`
- graphique patrimoine
- `SCI Overview`
- `Top Biens`

## Raison du changement

- Corriger un calcul trop strict sur `valeur_actuelle`
- Afficher une valorisation exploitable quand seule la valeur d'acquisition est connue
- Réduire les blocs dashboard à zéro artificiel

## Tests effectués

- Relecture ciblée des calculs dashboard
- vérification du diff sur `dashboard_service.py`
- `python -m py_compile backend/app/services/dashboard_service.py`

## Limites de validation

La lecture directe de la base locale n'a pas pu être vérifiée depuis le sandbox car l'accès PostgreSQL local était bloqué.
Le diagnostic repose donc sur le code métier et sur la logique de calcul observée.

## Impact sur l'architecture

- Le dashboard valorise désormais les biens à partir de la meilleure source disponible :
  `valeur_actuelle` si présente, sinon `prix_acquisition`.
