# Refactor Payment Status Sync Locataire Bien - 2026-03-25

## Description de la modification

Après marquage d'une quittance comme payée, le statut locataire restait affiché en `retard`.
La cause était un mauvais mapping backend entre les statuts ORM réels (`paye`, `impaye`)
et les libellés frontend attendus.

Le refactor :
- corrige le mapping locataire
- expose le statut de paiement sur les biens
- affiche ce statut dans l'onglet Biens

## Fichiers impactés

### d=1 — Appelants / fichiers directement affectés
- `backend/app/services/patrimoine_service.py`
- `backend/app/schemas/bien_schema.py`
- `frontend/lib/types/index.ts`
- `frontend/components/admin/tabs/BiensTab.tsx`

### d=2 — Dépendances indirectes à surveiller
- `backend/app/api/bien_routes.py`
- `backend/app/api/locataire_routes.py`
- `frontend/components/admin/tabs/LocatairesTab.tsx`

### d=3 — Zones transverses pouvant nécessiter revalidation
- tableau Locataires
- tableau Biens
- badges de paiement liés au bail actif

## Raison du changement

- corriger un statut faux après paiement
- refléter le paiement à la fois sur le locataire et sur le bien concerné
- garder une vue cohérente entre modules admin

## Tests effectués

- `python -m py_compile` sur `patrimoine_service.py` et `bien_schema.py`
- exécution directe de `PatrimoineService.get_all_locataires()` et `get_all_biens()` sur la base locale

## Résultat constaté

Après correction :
- locataire : `statut_paiement = a_jour`
- bien : `statut_paiement = a_jour`

## Impact sur l'architecture

- Le statut de paiement n'est plus uniquement visible au niveau locataire ; il remonte aussi au niveau bien.
- Le mapping backend/frontend des statuts quittance est désormais cohérent.
