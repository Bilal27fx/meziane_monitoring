# Refactor: native quittance PDF generator

## Description de la modification

- Suppression de la dépendance runtime à `fpdf` pour la génération de quittance.
- Remplacement par un générateur PDF minimal natif en Python standard library.
- Le téléchargement PDF fonctionne désormais sans rebuild du conteneur backend.

## Fichiers impactés

### d=1 — WILL BREAK / appelants directs

- `backend/app/api/quittance_routes.py`
- `backend/app/main.py`

### d=2 — LIKELY AFFECTED

- Route `GET /api/quittances/{id}/pdf`
- Interface locataire qui déclenche le téléchargement

### d=3 — MAY NEED TESTING

- Lecture du PDF dans différents navigateurs
- Upload MinIO après génération locale

## Raison du changement

- Le backend actif ne contenait pas `fpdf`, ce qui rendait le téléchargement de quittance indisponible.
- Un fallback 503 remettait l'API debout, mais ne résolvait pas le besoin utilisateur.

## Tests effectués

- `python -m py_compile backend/app/api/quittance_routes.py`
- Validation via le conteneur backend que `_build_quittance_pdf()` renvoie un flux commençant par `%PDF-1.4`

## Impact sur l'architecture

- La génération PDF ne dépend plus d'une librairie externe au runtime.
- Le contrat API reste inchangé.
