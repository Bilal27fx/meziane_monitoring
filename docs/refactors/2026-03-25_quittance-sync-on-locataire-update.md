# Refactor: quittance sync on locataire update

## Description de la modification

- Synchronisation des quittances ouvertes quand le bail actif d'un locataire est modifié.
- Le PDF de quittance recalcule le montant courant a partir du bail actif au moment du téléchargement.
- Le nom de fichier téléchargé vient maintenant du backend pour rester cohérent avec les données réellement utilisées.

## Fichiers impactés

### d=1 — WILL BREAK / appelants directs

- `backend/app/services/patrimoine_service.py`
- `backend/app/api/quittance_routes.py`
- `frontend/components/admin/panels/QuittancesPanel.tsx`

### d=2 — LIKELY AFFECTED

- Mise à jour d'un locataire avec changement de loyer ou de charges
- Route `GET /api/quittances/{id}/pdf`
- Panneau quittances depuis l'onglet locataires

### d=3 — MAY NEED TESTING

- Modification d'un bail actif avec quittance déjà existante
- Changement de nom/prénom locataire puis nouveau téléchargement
- Affichage du total quand `loyer + charges` diffère de l'ancien snapshot

## Raison du changement

- Les quittances existantes pouvaient conserver un ancien snapshot des montants.
- Le téléchargement PDF pouvait donc ne pas refléter immédiatement les données mises à jour du locataire et du bail.
- Le besoin utilisateur est d'afficher le total reçu attendu, par exemple `700 + 100 = 800`.

## Tests effectués

- `python -m py_compile backend/app/api/quittance_routes.py`
- Relecture ciblée de `PatrimoineService.update_locataire()`
- Relecture ciblée du flux `QuittancesPanel -> GET /api/quittances/{id}/pdf`

## Impact sur l'architecture

- Les quittances non finalisées deviennent un snapshot recalculable à partir du bail actif.
- Le backend reste la source de vérité pour le nom exact du fichier PDF téléchargé.
