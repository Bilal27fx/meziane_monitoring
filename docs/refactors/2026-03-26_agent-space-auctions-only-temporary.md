# Refactor: Agent Space Auctions Only Temporary

Date: 2026-03-26

## Contexte

L'espace `/agent` montait encore les panneaux legacy:

- prospection
- taches
- logs

Ces panneaux appelaient des endpoints inexistants sur ce backend:

- `/api/agent/opportunites`
- `/api/agent/config`
- `/api/agent/tasks`
- `/api/agent/logs`

Resultat:

- bruit 404 permanent dans les logs backend
- pollution inutile de l'observabilite

## Changement

`frontend/components/agent/AgentTabs.tsx` est recentre temporairement sur:

- `Encheres`
- un panneau `Legacy` purement informatif

Les composants legacy ne sont plus montes automatiquement, donc leurs hooks ne
pollent plus les endpoints `/api/agent/*`.

## Impact

- les logs backend ne doivent plus etre pollues par des `404` sur `/api/agent/*`
- l'espace agent est aligne avec le seul domaine reellement branche aujourd'hui:
  les enchères

## Suite logique

- soit recreer un vrai backend `/api/agent/*`
- soit supprimer definitivement les panneaux legacy
