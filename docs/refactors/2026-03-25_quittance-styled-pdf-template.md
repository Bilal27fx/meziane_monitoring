# Refactor: quittance styled PDF template

## Description de la modification

- Remplacement du rendu PDF minimal par un template plus sobre et plus professionnel.
- Conservation des accents dans le texte PDF via un encodage latin-1 direct au lieu d'une normalisation qui les supprimait.
- Correction de l'encodage PDF des polices standard avec `WinAnsiEncoding` pour que les accents s'affichent correctement.
- Simplification de la mise en page: hiérarchie typographique plus nette, blocs plus discrets, palette plus neutre.
- Réduction du nombre de blocs pour un rendu plus simple et moins fragile.
- Le nom du fichier téléchargé suit désormais `locataire + période` sans supprimer les accents.
- Normalisation ASCII du texte visible dans le PDF pour éviter les régressions d'affichage liées aux accents.
- Réduction de la taille du bloc `Montant total regle`.
- Le téléchargement de quittance sert maintenant le template courant a chaque requete pour que le nouveau design soit visible aussi sur les quittances deja existantes.

## Fichiers impactes

### d=1 — WILL BREAK / appelants directs

- `backend/app/api/quittance_routes.py`
- `frontend/components/admin/panels/QuittancesPanel.tsx`

### d=2 — LIKELY AFFECTED

- Route `GET /api/quittances/{id}/pdf`
- Telechargement des quittances depuis le panneau locataire

### d=3 — MAY NEED TESTING

- Rendu visuel sur Chrome, Safari et apercu macOS
- Quittances avec noms de SCI ou adresses longues
- Statuts `en_attente`, `paye`, `impaye`, `partiel`

## Raison du changement

- Le template precedent etait fonctionnel mais trop demonstratif visuellement.
- Les accents etaient perdus dans les libelles et les textes de quittance.
- Le besoin utilisateur est d'obtenir une quittance plus raffinee, simpliste et professionnelle.

## Tests effectues

- `python -m py_compile backend/app/api/quittance_routes.py`
- Verification manuelle du flux de generation dans `backend/app/api/quittance_routes.py`
- Tentative de test runtime direct de `_build_quittance_pdf()` bloquee localement par l'absence de la dependance `jose`
- Correctif d'un bug de shadowing sur la couleur de bordure qui provoquait un `500` a la generation PDF

## Impact sur l'architecture

- Aucun changement de route publique.
- Le backend continue de generer les PDF sans dependance externe de rendu.
- La route de telechargement ne depend plus du fichier precedent stocke pour afficher le design courant.
