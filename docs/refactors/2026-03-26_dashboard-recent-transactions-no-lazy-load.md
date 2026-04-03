# 2026-03-26 — Dashboard recent transactions sans lazy-load

## Contexte

Le service dashboard récupérait les dernières transactions via `query(Transaction).join(...)`, puis lisait `tx.sci.nom` et `tx.bien.adresse` sur les objets ORM.

Cette structure masque un coût évitable:

- la requête principale charge les transactions
- les accès aux relations peuvent repartir en lazy-load
- sur un endpoint dashboard très consulté, cela crée un surcoût SQL inutile

## Changement

- réécriture de `DashboardService.get_recent_transactions()`
- sélection explicite des colonnes nécessaires:
  - `Transaction.*` utiles à l'affichage
  - `SCI.nom`
  - `Bien.adresse`
- suppression de la dépendance à `tx.sci` et `tx.bien` dans la phase de mapping

## Fichiers impactés

- `backend/app/services/dashboard_service.py`
- `backend/tests/services/test_dashboard_service.py`

## Analyse d'impact

Analyse d'impact manuelle réalisée avant édition:

- symbole touché: `DashboardService.get_recent_transactions`
- d=1:
  - endpoint `GET /api/dashboard/transactions`
  - `DashboardService.get_full_dashboard()`
- d=2:
  - widget transactions du dashboard
  - chargement du dashboard complet

Risque estimé: `MEDIUM`

## Bénéfice

- suppression d'un lazy-load évitable
- lecture dashboard plus stable sous charge
- mapping de réponse plus explicite et moins couplé aux relations ORM

## Tests effectués

- ajout d'un test de service qui vérifie:
  - les données retournées
  - une seule requête `SELECT` pour construire le payload d'affichage
- validation dans le conteneur backend:

```bash
docker-compose exec -T backend pytest tests/services/test_dashboard_service.py tests/api/test_document_routes.py
```

Résultat: `4 passed`
