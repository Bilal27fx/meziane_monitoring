# 2026-03-25 — Refactor séparation du domaine quittance

## Pourquoi

Le domaine quittance concentre aujourd'hui plusieurs responsabilités sensibles dans un seul point: règles métier, génération PDF, nommage de fichier, accès MinIO et logique HTTP. Cette concentration augmente fortement le risque de régression.

## Problèmes ciblés

- route trop volumineuse
- PDF généré dans la couche HTTP
- logique de stockage mêlée au métier quittance
- comportement difficile à tester unitairement

## Ce qu'il faut faire

- garder `quittance_routes.py` très fin
- créer un service métier `quittance_service.py`
- créer un service technique `quittance_pdf_service.py`
- centraliser la gestion du stockage PDF dans un service dédié
- garder les tâches batch de génération dans `tasks/` uniquement si elles sont réellement asynchrones

## Répartition conseillée

- route:
  validation HTTP, auth, codes de retour, streaming
- service métier:
  génération, synchronisation, état payé/partiel/impayé, recalcul montants
- service PDF:
  rendu, encodage, style, contenu textuel
- service stockage:
  upload, existence, récupération, régénération si objet absent

## Bénéfice

- corrections PDF moins risquées
- code quittance plus testable
- dépendances externes mieux isolées
