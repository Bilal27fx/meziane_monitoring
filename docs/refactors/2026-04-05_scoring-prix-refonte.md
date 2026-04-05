# Refactor — Refonte scoring prix v2

**Date :** 2026-04-05  
**Fichiers modifiés :**
- `backend/app/services/auction_scoring_config.json`
- `backend/app/services/auction_scoring_service.py`
- `backend/tests/services/test_auction_scoring_service.py`

---

## Problème

Le score prix était structurellement cassé : il calculait `prix_estime_enchere / valeur_prudente` avec `prix_estime = reserve × 1.7`. Ce multiplicateur écrasait toute décote judiciaire réelle. Résultat : **100% des biens obtenaient score_prix = 25** (plancher), rendant cette dimension inutile.

En parallèle, le deal_breaker `-12` se déclenchait sur presque tous les biens car il utilisait `reserve × 1.7 × 1.1 + travaux > valeur_prudente × 1.12` — seuil quasi systématiquement dépassé.

---

## Solution

### Nouvelle architecture scoring — 5 dimensions indépendantes

| Dimension | Poids | Calcul |
|-----------|-------|--------|
| Localisation | 25% | `location_bases[cluster] + micro_bonus_llm` |
| Surface | 20% | Grille surface_scores (cœur de cible 18-35m²) |
| **Prix** | 30% | `(reserve_price / surface_m2) / prix_m2_reference_location` |
| Composition | 15% | Typologie cible + état + annexes (remplace score_qualite) |
| Occupation | 10% | Libre=100, Occupé=30, Inconnu=45 |

### Nouveaux brackets score_prix (ratio mise à prix / m² vs marché)

```
< 35% du marché  → 100
35–50%           →  85
50–65%           →  65
65–80%           →  40
80–100%          →  15
> 100%           →   0
```

Le multiplicateur 1.7× est **conservé uniquement pour prix_interessant / prix_palier**, pas pour le scoring.

### Deal_breakers simplifiés

- `surface < 12` : -25
- `reserve × 1.1 + travaux > valeur_prudente × 1.05` : -15 (cap 50) — condition sur la mise à prix réelle
- `occupation inconnu` : -2

Supprimé : `"prix_estime > valeur_marche"` (basé sur 1.7×, se déclenchait partout).

### Correction bug field mapping

`valeur_marche_ajustee` stockait `valeur_prudente` — corrigé. `AuctionScoringBreakdown` a maintenant un champ `valeur_prudente` séparé.

### Simplification score_listing

Suppression du double calcul `_deal_breaker_penalty` dans `score_listing` (re-calculait avec `valeur_marche_ajustee` au lieu de `valeur_prudente`). Les pénalités sont maintenant stockées dans `AuctionScoringBreakdown` et lues directement.

---

## Impact attendu (exemples des logs avant refonte)

| Bien | Avant | Après estimé |
|------|-------|--------------|
| Paris studio 19m², reserve=78k | prix=25 (plancher) | prix≈85 (ratio 0.37) |
| Boulogne T2 20m², reserve=52k | prix=25 | prix=100 (ratio 0.34) |
| Colombes T2 24m², reserve=89k | prix=25 | prix≈65 (ratio 0.49) |
| Evry T4 62m², reserve=280k | prix=25 | prix=0 (ratio 1.33) |

---

## Tests

14/14 tests passent. Seuils mis à jour pour refléter la nouvelle logique.
