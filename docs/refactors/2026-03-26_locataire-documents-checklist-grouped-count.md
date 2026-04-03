# 2026-03-26 — Checklist documents locataire avec comptage agrégé SQL

## Contexte

L'endpoint de checklist documents locataire chargeait tous les documents du locataire en mémoire pour calculer ensuite un compteur par type en Python.

Ce comportement n'est pas scalable:

- coût mémoire proportionnel au nombre de documents
- surcharge CPU côté application pour un calcul simple
- aucune nécessité de rapatrier toutes les lignes pour un simple comptage

## Changement

- remplacement du chargement complet `Document.query(...).all()` par une agrégation SQL
- usage de:
  - `GROUP BY Document.type_document`
  - `COUNT(Document.id)`
- conservation du même contrat HTTP de réponse

## Fichiers impactés

- `backend/app/api/document_routes.py`
- `backend/tests/api/test_document_routes.py`

## Analyse d'impact

Analyse d'impact manuelle réalisée avant édition:

- symbole touché: `get_locataire_documents_checklist`
- d=1:
  - endpoint `GET /api/documents/locataire/{locataire_id}/checklist`
- d=2:
  - toute UI future ou existante consommant la checklist locataire

Risque estimé: `LOW`

## Bénéfice

- réduction du volume de données chargées
- coût plus stable quand un locataire possède beaucoup de documents
- endpoint mieux aligné avec un usage de lecture agrégée

## Tests effectués

- ajout d'un test API qui vérifie:
  - les compteurs retournés
  - la présence d'une requête SQL agrégée avec `GROUP BY` et `COUNT`
- validation dans le conteneur backend:

```bash
docker-compose exec -T backend pytest tests/services/test_dashboard_service.py tests/api/test_document_routes.py
```

Résultat: `4 passed`
