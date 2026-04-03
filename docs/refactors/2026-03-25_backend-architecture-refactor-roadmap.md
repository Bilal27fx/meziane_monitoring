# 2026-03-25 — Roadmap refactor architecture backend

## Objectif

Faire évoluer le backend actuel vers une structure plus stable et plus scalable sans sortir du monolithe FastAPI ni introduire de complexité inutile.

## Constats

- plusieurs services de liste font des requêtes dans des boucles, ce qui crée du `N+1`
- certaines routes portent trop de logique métier et de logique technique dans le même fichier
- certains schémas API dérivent trop fortement la réponse attendue par le frontend
- il n'y a pas de base de tests backend suffisante pour sécuriser les régressions
- l'initialisation de l'application est encore très centralisée et fragile
- le domaine documents est encore trop orienté `type_document` métier alors que le besoin produit est surtout `créer un dossier` puis `uploader librement`

## Direction retenue

- garder un monolithe unique
- garder FastAPI, SQLAlchemy, Alembic, Celery et MinIO
- ne pas introduire de microservices
- ne pas introduire de repository générique sur tout le codebase
- séparer plus clairement `api`, `services`, `queries` et `integrations`
- simplifier le domaine documents autour d'une bibliothèque de fichiers et dossiers, pas autour d'une taxonomie imposée

## Ordre conseillé

1. sécuriser les contrats API et ajouter un socle de tests backend
2. extraire les requêtes de lecture lourdes hors des services métier
3. refondre le domaine documents en `dossiers + documents`
4. découper le domaine quittance en services dédiés
5. fiabiliser l'initialisation app et les intégrations externes

## Cible de structure

- `app/api/`
  routes HTTP fines, validation d'entrée, erreurs HTTP, pas de métier lourd
- `app/services/`
  cas d'usage métier: paiements, documents, quittances, transactions, patrimoine
- `app/queries/`
  lecture optimisée pour dashboard, listes, agrégations et vues admin
- `app/schemas/`
  contrats API stricts et stables
- `app/integrations/`
  stockage, connecteurs bancaires, dépendances externes
- `app/tasks/`
  tâches asynchrones réellement lentes ou batch

## Refactors liés

- [2026-03-25_backend-api-contracts-and-tests.md](./2026-03-25_backend-api-contracts-and-tests.md)
- [2026-03-25_backend-read-model-query-split.md](./2026-03-25_backend-read-model-query-split.md)
- [2026-03-25_documents-folders-and-free-upload.md](./2026-03-25_documents-folders-and-free-upload.md)
- [2026-03-25_quittance-domain-separation.md](./2026-03-25_quittance-domain-separation.md)
- [2026-03-25_backend-bootstrap-and-integrations-hardening.md](./2026-03-25_backend-bootstrap-and-integrations-hardening.md)

## Résultat attendu

- moins de régressions backend visibles côté UI
- moins de requêtes inutiles sur les écrans de liste
- un module documents plus simple à utiliser et plus proche du comportement attendu
- fichiers métier plus testables
- structure plus lisible pour continuer à ajouter des fonctionnalités sans casser l'existant
