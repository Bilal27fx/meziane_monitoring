# MERCATO — Agent Prix Marché

**Rôle :** Estimation du prix marché au m² par listing via données DVF  
**LLM :** Optionnel — gpt-4o-mini (interprétation si données insuffisantes)  
**Position dans le graphe :** HERMES → MERCATO (en parallèle avec ARCHIVIO) → ORACLE

---

## Responsabilité

MERCATO enrichit chaque listing avec une estimation du prix marché réel au m²
dans le quartier, en interrogeant l'API DVF (Demandes de Valeurs Foncières).

Il calcule le **ratio mise_a_prix / prix_marché** qui est la donnée la plus critique
pour ORACLE : un ratio bas = opportunité, un ratio élevé = sur-évalué.

Ses erreurs sont non-bloquantes — si DVF ne répond pas, ORACLE continue sans prix marché.

---

## Ce qu'il reçoit (depuis le state)

```python
raw_listings: list[dict]
# Utilisé : source_url, postal_code, city, surface_m2, reserve_price
```

---

## Ce qu'il produit (dans le state)

```python
price_estimates: dict[str, dict]
# listing_url → {
#   "prix_m2_marche": 8500.0,         # prix médian marché €/m²
#   "prix_m2_mise_a_prix": 2069.0,    # reserve_price / surface_m2
#   "ratio": 0.24,                    # mise_a_prix / prix_marche (< 0.7 = opportunité)
#   "nb_transactions": 42,            # nb ventes DVF dans le rayon
#   "rayon_metres": 500,
#   "periode_mois": 24,               # fenêtre temporelle des transactions
#   "source": "dvf",                  # "dvf" | "dvf+llm" | "unavailable"
#   "confidence": "high"              # "high" | "medium" | "low"
# }
```

---

## Séquence interne

```
Pour chaque listing dans raw_listings :
  1. Extraire postal_code + surface_m2 + reserve_price
  2. Appel API DVF (api.gouv.fr/datasets/demandes-de-valeurs-foncieres)
     → Transactions immobilières dans un rayon de 500m, 24 derniers mois
     → Filtrer par type (appartement/maison) et surface comparable (±30%)
  3. Calculer prix médian au m²
  4. Calculer ratio = reserve_price / (surface_m2 * prix_m2_marche)
  5. Si < 5 transactions → confidence = "low", rayon élargi à 1000m
  6. Si toujours insuffisant → source = "unavailable"
```

---

## Fichiers

```
backend/app/agents/mercato/
├── __init__.py
├── agent.py        # mercato_node(state) → dict partiel
└── dvf_client.py   # Client API DVF avec cache + retry
```

---

## API DVF

**Source :** `https://api.gouv.fr/les-api/api-dvf`  
**Endpoint principal :** `GET /transactions` avec filtres géographiques  
**Pas de clé API requise** (données publiques)

```python
# Exemple de requête
GET /transactions?code_postal=75011&type_local=Appartement&date_min=2024-01-01
```

**Cache** : résultats mis en cache 24h par `(postal_code, type_bien)` pour éviter
de re-requêter DVF pour des listings dans le même arrondissement.

---

## Interprétation du ratio

| Ratio | Interprétation |
|-------|---------------|
| < 0.50 | Très forte opportunité |
| 0.50 – 0.65 | Bonne opportunité |
| 0.65 – 0.80 | Opportunité correcte |
| 0.80 – 1.00 | Proche du marché |
| > 1.00 | Sur-évalué |

Ces seuils sont utilisés par ORACLE dans son scoring.

---

## Contraintes

- **Non-bloquant** : si DVF échoue, `price_estimates[listing_url] = {"source": "unavailable"}`
- **Timeout DVF** : 10s par requête
- **Retry** : 2 tentatives
- **Cache** : 24h en mémoire (ou Redis si disponible)
- **Parallèle** : tous les listings traités en asyncio.gather()

---

## Erreurs dans le state

```python
{"node": "mercato", "detail": "DVF API timeout for postal_code 75011", "ts": "..."}
{"node": "mercato", "detail": "0 transactions found for 75020, confidence=low", "ts": "..."}
```
