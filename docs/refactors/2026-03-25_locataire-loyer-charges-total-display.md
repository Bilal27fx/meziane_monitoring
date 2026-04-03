# 2026-03-25 — Affichage total loyer + charges dans la liste locataires

## Contexte

Dans l'onglet locataires, la colonne `Loyer` affichait uniquement `loyer_mensuel`, alors que l'utilisateur attend le total mensuel facturé.

## Changement

- calcul du montant affiché avec `loyer_mensuel + charges_mensuelles`
- conservation du fallback `—` si aucun bail n'est rattaché au locataire

## Impact

- frontend uniquement
- portée limitée au tableau admin des locataires
