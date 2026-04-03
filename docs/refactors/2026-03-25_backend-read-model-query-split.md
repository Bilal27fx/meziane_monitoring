# 2026-03-25 — Refactor read models et séparation des requêtes

## Pourquoi

Les écrans de liste et de synthèse utilisent aujourd'hui des services métier qui reconstruisent les données en multipliant les requêtes. Cette approche reste acceptable à petite taille, mais elle devient rapidement coûteuse sur les SCI, biens, locataires et vues dashboard.

## Problèmes ciblés

- requêtes dans des boucles
- calculs de lecture mélangés au métier d'écriture
- duplication de logique de synthèse entre dashboard, patrimoine et locataires

## Ce qu'il faut faire

- créer `app/queries/` pour les lectures optimisées
- extraire les vues de liste hors de `PatrimoineService`
- utiliser `join`, `outerjoin`, `joinedload`, agrégations SQL et sous-requêtes ciblées
- retourner des DTO simples dédiés aux écrans de lecture

## Modules à traiter en premier

- patrimoine
- locataires
- dashboard
- transactions

## Exemple de découpage

- `app/queries/patrimoine_queries.py`
- `app/queries/locataire_queries.py`
- `app/queries/dashboard_queries.py`
- `app/queries/transaction_queries.py`

## Règle de design

- `services/` pour le métier et les mutations
- `queries/` pour les lectures enrichies et optimisées
- pas de couche repository générique

## Bénéfice

- meilleure performance sur les listes
- responsabilité plus claire par module
- requêtes plus faciles à profiler et à tester
