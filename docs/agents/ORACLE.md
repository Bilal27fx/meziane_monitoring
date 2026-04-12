# ORACLE — Agent Décision

**Rôle :** Score multi-dimensionnel + décision BUY / WATCH / SKIP  
**LLM :** Oui — gpt-4o  
**Position dans le graphe :** [ARCHIVIO, MERCATO] → ORACLE → PERSIST

---

## Responsabilité

ORACLE reçoit toutes les données collectées (listing brut, PDF, prix marché)
et produit pour chaque annonce :
- Un **score numérique** (0–100)
- Une **décision** : `BUY` / `WATCH` / `SKIP`
- Une **justification textuelle** courte (3–5 phrases)
- Un **breakdown** des dimensions scorées

C'est le seul agent qui synthétise l'ensemble des données.
Il utilise gpt-4o (plus précis que mini) car la décision est critique.

---

## Ce qu'il reçoit (depuis le state)

```python
raw_listings: list[dict]          # données brutes HERMES
pdf_extractions: dict[str, dict]  # données PDF ARCHIVIO (peut être null par listing)
price_estimates: dict[str, dict]  # données marché MERCATO (peut être null par listing)
```

---

## Ce qu'il produit (dans le state)

```python
scored_listings: list[dict]
# [
#   {
#     "listing_url": "https://licitor.fr/annonce/456",
#     "score": 78,
#     "decision": "BUY",
#     "justification": "Mise à prix 35% sous le marché pour un T3 libre de 58m²
#                       en bon état. Cave incluse, DPE D acceptable. Visite
#                       possible le 1er mai. Ratio exceptionnel pour Paris 11.",
#     "breakdown": {
#       "ratio_prix": 35,          # /35 — poids le plus fort
#       "surface_type": 15,        # /15
#       "etat_bien": 10,           # /10
#       "occupation": 10,          # /10 (libre = max)
#       "localisation": 10,        # /10
#       "visite_possible": 10,     # /10
#       "donnees_pdf": 10          # /10 (bonus si données PDF disponibles)
#     },
#     "deal_breakers": [],         # ["occupé", "surface<20m2", ...]
#     "flags": ["visite_imminente", "ratio_exceptionnel"]
#   }
# ]
```

---

## Dimensions de scoring

| Dimension | Poids max | Source données |
|-----------|-----------|----------------|
| Ratio prix (mise_a_prix / marché) | 35 | MERCATO |
| Surface et type de bien | 15 | HERMES |
| État général du bien | 10 | ARCHIVIO |
| Statut occupation (libre/occupé) | 10 | HERMES |
| Localisation (ville, arrondissement) | 10 | HERMES |
| Visite possible avant enchère | 10 | HERMES |
| Richesse données PDF disponibles | 10 | ARCHIVIO |
| **Total** | **100** | |

### Deal breakers (score forcé à 0, décision SKIP)

- Surface < 15m²
- Bien occupé ET prix marché non exceptionnel (ratio > 0.6)
- Pas de date d'enchère connue
- Tribunal hors zone cible

---

## Séquence interne

```
Pour chaque listing dans raw_listings :
  1. Récupérer pdf_extractions[listing_url] → peut être None
  2. Récupérer price_estimates[listing_url] → peut être None
  3. Vérifier deal_breakers → si déclenché, score=0, decision=SKIP, stop
  4. Calculer chaque dimension de score
  5. Appel LLM gpt-4o pour générer la justification textuelle
     (les scores sont calculés en Python, le LLM ne fait que la prose)
  6. Déterminer la décision :
     score >= 70 → BUY
     score >= 45 → WATCH
     score < 45  → SKIP
  7. Détecter les flags (visite_imminente si < 7 jours, ratio_exceptionnel si < 0.5)
```

**Important** : le score est calculé algorithmiquement en Python.
Le LLM est appelé **uniquement pour la justification textuelle**.
Cela garantit des scores reproductibles et traçables.

---

## Fichiers

```
backend/app/agents/oracle/
├── __init__.py
├── agent.py    # oracle_node(state) → dict partiel
└── scorer.py   # Logique de scoring Python (déterministe, sans LLM)
```

---

## Prompt LLM (justification)

**Modèle :** `gpt-4o`  
**Température :** `0.3`  
**Tokens max :** `200`

Le prompt reçoit le breakdown des scores et les données du listing.
Il produit uniquement la justification en français (3–5 phrases).
Il ne recalcule pas le score — il l'explique.

---

## Contraintes

- **Bloquant** : si ORACLE échoue sur un listing, il logge l'erreur et continue sur le suivant
- **Bloquant global** : si ORACLE échoue sur tous les listings, le run échoue
- **Timeout LLM** : 20s par justification
- **Pas de LLM si SKIP** : la justification SKIP est générée sans LLM (template fixe)

---

## Décision et seuils

```python
DECISION_THRESHOLDS = {
    "BUY":   70,   # Score >= 70 → notifier immédiatement
    "WATCH": 45,   # Score >= 45 → enregistrer, pas de notif
    "SKIP":  0     # Score < 45  → enregistrer, ignorer
}
```

Ces seuils sont configurables dans un fichier de config (pas en dur dans le code).

---

## Flags automatiques

| Flag | Condition |
|------|-----------|
| `visite_imminente` | Visite dans les 7 prochains jours |
| `ratio_exceptionnel` | Ratio < 0.50 |
| `enchère_imminente` | Date enchère dans les 14 prochains jours |
| `données_incomplètes` | PDF absent ET prix marché indisponible |

---

## Erreurs dans le state

```python
{"node": "oracle", "detail": "LLM justification timeout for listing 456", "ts": "..."}
```
