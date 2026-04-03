# 2026-03-25 — Dashboard transactions routing and sort fix

## Contexte

Deux incohérences existaient autour des transactions :

- le lien `Voir toutes` du widget dashboard ouvrait `/admin` sans cibler l'onglet transactions
- la liste paginée des transactions triait seulement par `date`, ce qui pouvait masquer une transaction récemment créée si plusieurs écritures partageaient la même date

## Changement

- le dashboard pointe maintenant vers `/admin?tab=transactions`
- l'admin lit `tab` dans l'URL pour ouvrir le bon onglet au chargement
- l'API liste des transactions trie désormais par `date desc`, puis `created_at desc`, puis `id desc`

## Impact

- frontend: navigation correcte depuis le dashboard vers l'onglet transactions
- backend: ordre de retour stabilisé pour faire remonter les transactions créées récemment
