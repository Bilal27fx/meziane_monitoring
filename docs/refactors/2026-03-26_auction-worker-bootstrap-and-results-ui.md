# 2026-03-26 - Auction worker bootstrap and results UI

## Contexte

Le run Licitor etait cree et dispatche depuis l'interface agent, mais aucun resultat n'apparaissait.
Deux problemes distincts bloquaient l'usage:

1. le worker Celery cassait avant execution de l'ingestion auctions a cause d'un bootstrap ORM incomplet;
2. l'UI `Encheres` affichait uniquement la timeline des runs, pas les annonces effectivement ingerees.

## Changements

### Backend

- ajout de `load_all_models()` dans `backend/app/models/__init__.py` pour centraliser l'enregistrement des mappers SQLAlchemy;
- appel de `load_all_models()` au demarrage de `backend/app/main.py`;
- appel de `load_all_models()` au demarrage de `backend/app/tasks/celery_app.py` afin que le worker charge aussi tous les modeles avant execution des tasks.

### Frontend

- ajout du type `AuctionListing` dans `frontend/lib/types/index.ts`;
- ajout du hook `useAuctionListings()` dans `frontend/lib/hooks/useAgent.ts`;
- enrichissement de `frontend/components/agent/AuctionRunsPanel.tsx` pour afficher les annonces visibles pour le run selectionne en plus de la timeline.

## Resultat

- le worker peut maintenant executer `run_auction_ingestion_task` sans erreur ORM;
- un run Licitor relance manuellement a termine avec succes;
- les annonces ingerees deviennent visibles dans l'onglet `Encheres`, au lieu d'un simple statut de run.

## Verification

- `docker-compose exec -T backend pytest tests/services/test_auction_ingestion_service.py tests/api/test_auction_foundation_routes.py`
  - resultat: `10 passed`
- verification runtime worker:
  - run `#1` execute avec succes
  - `sessions_created=1`
  - `listings_created=1`
  - `listings_normalized=1`

## Limites

- la vue frontend filtre actuellement les resultats de maniere temporelle autour du run selectionne; une liaison explicite `run -> listings` sera preferable dans une prochaine tranche.
- la validation frontend par `npm run build` reste bloquee par des problemes d'environnement deja presents dans le repo.
