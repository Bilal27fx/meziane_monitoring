# 2026-03-25 — Alignement du domaine documents actif

## Contexte

Le refactor `dossier + document` était déjà engagé, mais le flux actif gardait encore des morceaux de l'ancien modèle piloté par `type_document`, avec un panneau SCI obsolète et un upload locataire passant encore par une route dédiée héritée.

## Changements effectués

- suppression du panneau frontend `DocumentsSCIPanel` non utilisé
- suppression des hooks frontend documents hérités non appelés par le flux actif
- suppression des constantes frontend de taxonomie documentaire devenues inutiles dans l'UI active
- bascule du formulaire locataire vers le hook d'upload générique `/api/documents/upload`
- ajout d'un nettoyage stockage MinIO lors de `DELETE /api/documents/{id}`
- ajout d'un test backend pour garantir la suppression de l'objet avant suppression de la ligne SQL

## Fichiers impactés

- `backend/app/api/document_routes.py`
- `backend/app/utils/storage.py`
- `backend/tests/api/test_document_routes.py`
- `frontend/components/admin/forms/LocataireForm.tsx`
- `frontend/lib/hooks/useAdmin.ts`
- `frontend/lib/types/index.ts`
- `frontend/components/admin/panels/DocumentsSCIPanel.tsx`

## Impact

- d=1 backend: suppression document désormais couplée au stockage MinIO
- d=1 frontend: les uploads post-création locataire passent par le flux générique aligné avec la bibliothèque documentaire
- d=2: réduction de dette et moindre risque de divergence entre panneau documents et contrat API actif

## Tests effectués

- ajout d'un test API backend sur la suppression document + nettoyage stockage
- vérifications locales de portée via recherche d'appelants (`rg`)

## Impact architectural

Le domaine actif se rapproche de la cible produit `dossier + fichier`, sans supprimer encore les routes de compatibilité backend qui peuvent rester le temps de terminer la transition.
