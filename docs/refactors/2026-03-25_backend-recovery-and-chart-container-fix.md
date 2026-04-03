# Refactor: backend recovery and chart container fix

## Description de la modification

- Suppression de la dépendance bloquante `fpdf` au chargement du module `quittance_routes.py`.
- Chargement paresseux de `fpdf` au moment de la génération PDF avec réponse HTTP 503 explicite si la dépendance n'est pas installée.
- Stabilisation des conteneurs Recharts du dashboard avec tailles minimales explicites pour éviter les warnings `width(-1)` / `height(-1)`.
- Rendu différé des graphiques après montage client pour éviter les mesures Recharts trop précoces.

## Fichiers impactés

### d=1 — WILL BREAK / appelants directs

- `backend/app/api/quittance_routes.py`
- `frontend/components/dashboard/CashflowChart.tsx`
- `frontend/components/dashboard/PatrimoineChart.tsx`
- `frontend/app/(app)/dashboard/page.tsx` (appelants directs des composants charts, contrat inchangé)
- `backend/app/main.py` (importe `quittance_routes` au démarrage)

### d=2 — LIKELY AFFECTED

- Flux backend de démarrage FastAPI / Uvicorn
- Route `GET /api/quittances/{id}/pdf`
- Vue dashboard frontend

### d=3 — MAY NEED TESTING

- Parcours utilisateur après redémarrage automatique du backend
- Affichage responsive des cartes dashboard

## Raison du changement

- Le backend redémarrait en boucle après modification du module PDF car `fpdf` n'était pas installé dans le conteneur actif.
- Les graphiques Recharts étaient montés dans des conteneurs sans dimensions suffisamment stables, provoquant des warnings navigateur répétés.

## Tests effectués

- `python -m py_compile backend/app/api/quittance_routes.py`
- Vérification des logs Docker backend après reload
- Vérification des logs Docker frontend pour absence de régression de compilation
- Les warnings Recharts doivent être revalidés après un refresh manuel du dashboard

## Impact sur l'architecture

- La génération PDF devient dégradée de façon sûre: l'absence d'une dépendance optionnelle ne doit plus empêcher toute l'API de démarrer.
- Les charts dashboard restent purement frontend, avec un contrat inchangé et un rendu plus robuste.
