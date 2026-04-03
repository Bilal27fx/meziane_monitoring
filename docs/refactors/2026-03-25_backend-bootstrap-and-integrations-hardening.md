# 2026-03-25 — Refactor bootstrap backend et durcissement des intégrations

## Pourquoi

Le backend fonctionne, mais son point d'entrée importe encore beaucoup de modules directement et certaines intégrations techniques restent trop rudimentaires pour accompagner la croissance du projet.

## Problèmes ciblés

- `main.py` centralise trop d'imports
- enregistrement des routes peu modulaire
- imports modèles utilisés comme mécanisme implicite de bootstrap
- client MinIO recréé à chaque appel
- vérifications techniques répétées dans le chemin nominal des requêtes

## Ce qu'il faut faire

- centraliser l'enregistrement des routers dans `app/api/__init__.py`
- centraliser les imports modèles dans `app/models/__init__.py`
- garder `main.py` concentré sur `FastAPI`, middleware, handlers et bootstrap
- encapsuler MinIO dans une intégration dédiée réutilisable
- préparer un logging un peu plus structuré pour les erreurs backend

## Ce qu'il ne faut pas faire

- ne pas introduire de framework DI supplémentaire
- ne pas ajouter d'observabilité lourde tout de suite
- ne pas transformer les intégrations simples en usine à abstractions

## Bénéfice

- startup plus lisible
- intégrations externes mieux contenues
- maintenance plus simple quand de nouveaux domaines métier seront ajoutés
