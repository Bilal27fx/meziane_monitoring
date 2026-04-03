# Refactor Header System Status - 2026-03-25

## Description de la modification

Le header affichait uniquement le titre de page et l'horloge, alors que la spec frontend
prévoit des badges de statut pour l'API et Celery.

Le refactor ajoute :
- un endpoint backend public `/health/services`
- un hook frontend de polling
- le branchement réel du header sur les badges `API` et `Celery`

## Fichiers impactés

### d=1 — Appelants / fichiers directement affectés
- `backend/app/main.py`
- `frontend/components/layout/Header.tsx`
- `frontend/lib/hooks/useSystemHealth.ts`
- `frontend/lib/types/index.ts`

### d=2 — Dépendances indirectes à surveiller
- `frontend/app/(app)/layout.tsx`
- `frontend/components/layout/StatusBadge.tsx`
- `backend/app/tasks/celery_app.py`

### d=3 — Zones transverses pouvant nécessiter revalidation
- rendu header sur Dashboard, Agent et Admin
- polling frontend en session authentifiée
- disponibilité réelle d'un worker Celery dans l'environnement local

## Raison du changement

- Aligner le header réel avec la spec `FRONTEND_ARCHITECTURE.md`
- Exposer un statut backend consommable par le frontend sans détour
- Donner un retour visuel immédiat sur la disponibilité API/Celery

## Tests effectués

- Relecture ciblée des endpoints de santé existants
- Vérification des usages du composant `Header`
- Vérification du diff sur les fichiers modifiés

## Limites de validation

Le build frontend global reste non validable localement dans cet environnement pour des raisons déjà présentes :
- dépendances frontend manquantes
- récupération Google Fonts bloquée

## Impact sur l'architecture

- Le header dépend maintenant d'un endpoint de santé dédié au lieu d'un état purement statique.
- Le backend expose un contrat minimal pour l'observabilité UI.
