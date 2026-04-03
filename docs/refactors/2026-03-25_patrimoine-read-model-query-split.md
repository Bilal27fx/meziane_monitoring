# 2026-03-25 — Patrimoine read model query split

## Contexte

Les listes `SCI`, `Biens` et `Locataires` étaient construites dans `PatrimoineService` avec des requêtes exécutées dans des boucles. Cette structure exposait le backend à un `N+1` rapide dès que le volume de données augmentait.

## Changement

- ajout d'une couche `app/queries/patrimoine_queries.py`
- extraction des lectures de liste `SCI`, `Biens` et `Locataires` hors du service métier
- usage de jointures et sous-requêtes agrégées pour récupérer les données en lecture enrichie
- conservation des mutations dans `PatrimoineService`

## Impact

- backend: séparation plus claire entre lecture et métier
- performance: baisse du nombre de requêtes sur les écrans admin de liste
- blast radius limité aux endpoints `/api/sci`, `/api/biens` et `/api/locataires`
