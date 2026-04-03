# Refactor: quittance MinIO self-heal

## Description de la modification

- Ajout d'une auto-réparation sur le téléchargement PDF de quittance.
- Si `fichier_url` existe en base mais que l'objet a été supprimé de MinIO, l'API régénère et ré-uploade automatiquement le PDF avant de le servir.

## Fichiers impactés

### d=1 — WILL BREAK / appelants directs

- `backend/app/api/quittance_routes.py`
- `frontend/components/admin/panels/QuittancesPanel.tsx`

### d=2 — LIKELY AFFECTED

- Route `GET /api/quittances/{id}/pdf`
- Téléchargement des quittances depuis le panneau locataire

### d=3 — MAY NEED TESTING

- Cas de suppression manuelle d'un objet quittance dans MinIO
- Cas d'URL de stockage invalide ou obsolète

## Raison du changement

- La liste UI des quittances vient de la base métier et non de MinIO.
- Une suppression manuelle dans MinIO laissait donc la quittance visible mais pouvait casser la récupération du fichier.

## Tests effectués

- `python -m py_compile backend/app/api/quittance_routes.py`
- Relecture du flux de réparation `fichier_url -> stat_object -> re-upload`

## Impact sur l'architecture

- Aucun changement de contrat API.
- Le stockage MinIO devient un cache/rendu régénérable au lieu d'un point de rupture unique.
