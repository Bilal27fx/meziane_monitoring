# Refactor: quittance download filename cors

## Description de la modification

- Exposition du header `Content-Disposition` via CORS.
- Alignement du nom de fichier quittance sur le format `nom-date.pdf`.
- Ajout d'un fallback frontend cohérent si le header n'est pas récupéré.

## Fichiers impactés

### d=1 — WILL BREAK / appelants directs

- `backend/app/main.py`
- `backend/app/api/quittance_routes.py`
- `frontend/components/admin/panels/QuittancesPanel.tsx`

### d=2 — LIKELY AFFECTED

- Téléchargement des quittances depuis le panneau locataire
- Toute lecture frontend du header `Content-Disposition`

### d=3 — MAY NEED TESTING

- Téléchargement sur Chrome et Safari
- Accents dans le nom de fichier
- Fallback frontend si le header est absent

## Raison du changement

- Le titre de fichier renvoyé par le backend n'était pas toujours repris côté navigateur.
- Le format attendu est `nom-date.pdf`.

## Tests effectués

- `python -m py_compile backend/app/api/quittance_routes.py`
- Relecture ciblée du flux `GET /api/quittances/{id}/pdf -> Content-Disposition -> a.download`

## Impact sur l'architecture

- Aucun changement d'API métier.
- Le backend devient la source de vérité pour le nom exact du fichier téléchargé.
