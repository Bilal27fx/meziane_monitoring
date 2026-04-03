# Refactor Quittance PDF Generation - 2026-03-25

## Description de la modification

Le bouton PDF des quittances ne fonctionnait pas car aucune génération réelle de PDF
n'existait derrière l'endpoint `/api/quittances/{id}/pdf`. En base, `fichier_url` restait
à `NULL`, et l'API renvoyait donc une erreur.

Le refactor ajoute :
- une génération PDF à la demande
- un stockage MinIO si disponible
- un fallback direct en streaming même si le stockage est indisponible

## Fichiers impactés

### d=1 — Appelants / fichiers directement affectés
- `backend/app/api/quittance_routes.py`
- `backend/requirements.txt`

### d=2 — Dépendances indirectes à surveiller
- `frontend/components/admin/panels/QuittancesPanel.tsx`
- `backend/app/utils/storage.py`
- environnement MinIO local

### d=3 — Zones transverses pouvant nécessiter revalidation
- téléchargement PDF des quittances
- rendu inline PDF dans le navigateur
- persistance de `fichier_url` en base

## Raison du changement

- corriger un bouton PDF non fonctionnel
- éviter le 404 quand aucun PDF n'a encore été généré
- rendre le flux robuste même si MinIO n'est pas accessible

## Tests effectués

- `python -m py_compile backend/app/api/quittance_routes.py`
- vérification en base : la quittance existait bien mais `fichier_url = NULL`

## Limites de validation

Le test end-to-end complet de l'endpoint via l'application active n'a pas été validé ici car
l'environnement Python utilisé en sandbox ne chargeait pas toutes les dépendances runtime de l'API.
La correction est néanmoins cohérente avec la base et valide syntaxiquement.

## Impact sur l'architecture

- Les quittances disposent maintenant d'un flux PDF autonome côté backend.
- L'API ne dépend plus strictement d'une URL pré-générée en base pour servir un PDF.
