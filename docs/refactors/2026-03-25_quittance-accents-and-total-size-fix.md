# Refactor: quittance accents and total size fix

## Description de la modification

- Restauration des accents dans le texte visible du PDF de quittance.
- Réduction supplémentaire de la taille typographique du bloc `Montant total réglé`.

## Fichiers impactés

### d=1 — WILL BREAK / appelants directs

- `backend/app/api/quittance_routes.py`

### d=2 — LIKELY AFFECTED

- Route `GET /api/quittances/{id}/pdf`
- Tous les téléchargements de quittance PDF

### d=3 — MAY NEED TESTING

- Affichage des accents dans les titres et paragraphes
- Lisibilité du bloc total sur macOS Preview et Chrome

## Raison du changement

- Le rendu PDF avait réintroduit une normalisation ASCII qui supprimait les accents.
- Le montant total devait aussi être visuellement moins dominant.

## Tests effectués

- `python -m py_compile backend/app/api/quittance_routes.py`

## Impact sur l'architecture

- Aucun changement d'API.
- Correctif purement backend sur le rendu PDF.
