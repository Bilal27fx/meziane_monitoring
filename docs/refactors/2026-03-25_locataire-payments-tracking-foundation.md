# 2026-03-25 — Fondation suivi paiements locataire

## Contexte

Le statut de paiement d'un locataire reposait surtout sur les quittances. Cela permettait un état mensuel simple, mais pas un vrai historique des règlements encaissés ni une synthèse fiable `payé / restant / derniers mois`.

## Changement

- ajout de la table `locataire_paiements` reliée au locataire, au bail et optionnellement à une quittance
- ajout d'une API dédiée sous `/api/locataires/{id}/paiements`
- synchronisation de `mark_quittance_paid` pour enregistrer aussi un paiement réel
- ajout d'un panneau frontend `Paiements` par locataire avec synthèse, historique mensuel complet, résumé annuel et graphe de visualisation
- les mois sans quittance existante sont désormais remontés comme échéances impayées dans l'historique
- ajout d'une validation directe par mois depuis le panneau, avec création automatique de la quittance si elle manque

## Impact

- backend: nouveau domaine métier pour tracer les encaissements
- base de données: migration Alembic requise
- frontend: nouveau point d'accès dans la liste locataires
