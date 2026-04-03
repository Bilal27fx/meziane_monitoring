# Refactor Quittance Mark Paid Action - 2026-03-25

## Description de la modification

Le panneau locataire affichait les quittances et permettait leur génération, mais aucune action
ne permettait de marquer une quittance comme payée.

Le refactor ajoute :
- un endpoint backend `POST /api/quittances/{id}/payer`
- un hook frontend dédié
- un bouton `Payée` dans le panneau des quittances

## Fichiers impactés

### d=1 — Appelants / fichiers directement affectés
- `backend/app/api/quittance_routes.py`
- `frontend/lib/hooks/useAdmin.ts`
- `frontend/components/admin/panels/QuittancesPanel.tsx`

### d=2 — Dépendances indirectes à surveiller
- `frontend/components/admin/tabs/LocatairesTab.tsx`
- `frontend/app/(app)/dashboard/page.tsx`
- `backend/app/schemas/quittance_schema.py`

### d=3 — Zones transverses pouvant nécessiter revalidation
- statut paiement locataires
- cartes locataires dashboard
- alertes liées aux impayés

## Raison du changement

- combler un manque fonctionnel dans la gestion locataire
- permettre la mise à jour explicite du statut d'une quittance
- refléter ce changement dans les vues locataires et dashboard

## Tests effectués

- `python -m py_compile backend/app/api/quittance_routes.py`
- vérification du diff sur backend + frontend

## Impact sur l'architecture

- La gestion des quittances devient bidirectionnelle : lecture/génération + mise à jour de statut.
- Les invalidations React Query propagent l'état payé vers les écrans locataires et dashboard.
