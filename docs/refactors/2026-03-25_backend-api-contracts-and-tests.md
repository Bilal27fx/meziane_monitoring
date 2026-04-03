# 2026-03-25 — Refactor contrats API et tests backend

## Pourquoi

Le backend a déjà subi des régressions causées par un décalage entre modèles ORM, schémas Pydantic et payloads réellement renvoyées au frontend. Sans socle de tests, ces écarts remontent tard et cassent l'admin.

## Problèmes ciblés

- schémas qui ne reflètent pas strictement les types du modèle
- transformation implicite trop forte dans certains `schema`
- absence de tests de contrat sur les endpoints critiques

## Ce qu'il faut faire

- revoir les schémas de réponse critiques pour qu'ils reflètent la vérité backend
- déplacer les mappings orientés frontend vers les services ou des adaptateurs explicites
- créer un dossier `backend/tests`
- ajouter des tests d'intégration ciblés sur les routes les plus sensibles

## Endpoints prioritaires

- `/api/transactions/`
- `/api/dashboard/full`
- `/api/locataires/{id}/paiements`
- `/api/quittances/{id}/pdf`
- `/api/auth/refresh`

## Livrables

- schémas backend stabilisés
- helpers de mapping explicites si une réponse doit être enrichie
- tests de route minimaux avec base de données de test
- tests de service pour les invariants métier les plus fragiles

## Non-objectifs

- couverture de test exhaustive
- refonte complète du frontend
- changement de framework de validation

## Bénéfice

Ce refactor réduit le risque de casser l'interface pour des erreurs de typage, de champ manquant ou de structure de réponse non conforme.
