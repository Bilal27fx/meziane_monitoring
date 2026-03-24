# Audit Scalabilité — Meziane Monitoring
**Date :** 2026-03-24
**Analysé via :** GitNexus MCP (1 630 symboles, 3 084 relations, 49 flows)
**Branche :** update&optimisation

---

## Résumé Exécutif

L'architecture actuelle est fonctionnelle pour un usage dev/démo mais présente **6 blocages critiques** qui empêcheront le passage à l'échelle dès les premiers vrais utilisateurs ou dès que le volume de données augmentera.

Les problèmes sont concentrés sur 4 fichiers :
- `backend/app/utils/db.py`
- `backend/app/services/dashboard_service.py`
- `backend/app/connectors/banking_connector.py`
- Migrations Alembic (absence d'index)

---

## Problèmes Critiques (P1)

### C1 — Aucun index DB sur les colonnes filtrées
**Fichiers :** `backend/alembic/versions/` (toutes les migrations)
**Impact :** Full table scan sur chaque requête dashboard

Les migrations ne contiennent aucun `CREATE INDEX`. Or les requêtes les plus fréquentes filtrent sur :
- `Transaction.date` — utilisé dans 8+ requêtes dashboard
- `Transaction.sci_id` / `Transaction.bien_id` — filtres principaux
- `Bail.statut` — filtré à chaque chargement locataires
- `Quittance.statut` + `Quittance.bail_id` — comptage alertes
- `Opportunite.statut` — flux agent IA

**Conséquence :** Avec 100 000 transactions → chaque appel `get_full_dashboard()` fera 20+ full table scans.

---

### C2 — Connection pool non configuré
**Fichier :** `backend/app/utils/db.py:23`

```python
# Actuel — pool par défaut SQLAlchemy : 5 connexions
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
```

SQLAlchemy par défaut : `pool_size=5`, `max_overflow=10`. Sous charge simultanée FastAPI + Celery + dashboard polling → saturation immédiate du pool → `TimeoutError` pour les utilisateurs.

De plus, `echo=settings.DEBUG` peut flooder les logs si `DEBUG=True` glisse en production.

---

### C3 — `get_kpi()` : 7 requêtes DB séquentielles
**Fichier :** `backend/app/services/dashboard_service.py:42-126`

```
get_kpi()
  ├── _calculate_patrimoine_net()    → 1 requête
  ├── _calculate_cashflow_today()    → 1 requête
  ├── _count_alertes()               → 2 requêtes (impayes + opportunites)
  ├── _calculate_performance_ytd()
  │     ├── get_global_cashflow()    → N requêtes (cashflow_service)
  │     └── _calculate_patrimoine_net() → 1 requête DUPLIQUÉE ← BUG
  ├── _calculate_taux_occupation()   → 2 requêtes (total + loués)
  └── _count_locataires_actifs()     → 1 requête
```

Total : **9 requêtes minimum** pour un seul endpoint KPI.
`get_full_dashboard()` appelle `get_kpi()` + 7 autres méthodes = **~25 requêtes par page load**.

---

### C4 — `get_cashflow_30days()` : agrégation Python en mémoire
**Fichier :** `backend/app/services/dashboard_service.py:149-195`

```python
# Charge TOUTES les transactions des 30 derniers jours en mémoire
transactions = self.db.query(Transaction).filter(...).all()
for tx in transactions:  # agrège en Python
    daily_data[day_key]["revenus"] += tx.montant
```

Avec 10 000 transactions/mois → 300 000 lignes chargées en RAM. Doit être un `GROUP BY CAST(date AS DATE)` côté DB.

---

### C5 — `get_top_biens_by_rentabilite()` : tri Python + slice
**Fichier :** `backend/app/services/dashboard_service.py:267-306`

```python
biens = self.db.query(Bien).filter(...).all()  # TOUS les biens chargés
result.sort(key=lambda x: x["rentabilite_nette"], reverse=True)
return result[:limit]  # on tronque après avoir tout chargé
```

Doit être `ORDER BY rentabilite_nette DESC LIMIT 5` côté SQL.

---

### C6 — `import_transactions_to_db()` : N×2 requêtes
**Fichier :** `backend/app/connectors/banking_connector.py:187-209`

```python
for raw_tx in raw_transactions:        # 100 transactions
    detect_duplicates(transaction_data) # 1 requête SELECT
    create_transaction(transaction_data) # 1 requête INSERT
# Total : 200 requêtes pour 100 transactions
```

Doit être un batch : 1 requête SELECT avec tous les IDs Bridge + 1 INSERT bulk.

---

## Problèmes Sécurité (P2)

### S1 — Credentials hardcodés dans le code source
**Fichier :** `backend/app/config.py:26, 34, 48`

```python
DATABASE_URL: str = "postgresql://meziane:meziane_dev_2026@localhost:5432/meziane_monitoring"
SECRET_KEY: str = "dev_secret_key_change_in_production"
MINIO_ACCESS_KEY: str = "minioadmin"
MINIO_SECRET_KEY: str = "minioadmin123"
```

Les valeurs par défaut sont en clair dans le code. Si le `.env` de production est absent → l'app démarre avec des credentials prévisibles.

---

### S2 — Health check `/health` factice
**Fichier :** `backend/app/main.py:87-93`

```python
return {"database": "connected", "redis": "connected"}  # jamais vérifié
```

Retourne toujours OK même si la DB est down. Inutilisable pour Kubernetes/Docker probes.

---

### S3 — Pas de rate limiting
Aucun middleware de throttling sur l'API. Le dashboard polling + un attaquant = surcharge immédiate.

---

## Problèmes de Fragilité (P3)

### F1 — `asyncio.new_event_loop()` dans Celery
**Fichier :** `backend/app/tasks/banking_tasks.py:38`

```python
loop = asyncio.new_event_loop()
try:
    ...
finally:
    loop.close()
```

Fragile, peut causer des fuites. `asyncio.run()` est plus propre et gère le cleanup automatiquement.

---

### F2 — Pas de timeout HTTP sur Bridge API
**Fichier :** `backend/app/connectors/banking_connector.py:49`

```python
async with httpx.AsyncClient() as client:  # timeout=None par défaut
```

Si Bridge API est lent ou down → worker Celery bloqué indéfiniment. Doit avoir `timeout=30.0`.

---

## Tableau de Synthèse

| ID | Fichier | Problème | Impact | Priorité |
|----|---------|----------|--------|----------|
| C1 | alembic/versions/ | Aucun index DB | Full table scan | 🔴 P1 |
| C2 | utils/db.py | Pool non configuré | Saturation connexions | 🔴 P1 |
| C3 | dashboard_service.py | 7+ requêtes séquentielles KPI | Lenteur dashboard | 🔴 P1 |
| C4 | dashboard_service.py | Agrégation cashflow en Python | OOM à l'échelle | 🔴 P1 |
| C5 | dashboard_service.py | Tri biens en Python | Charge mémoire | 🔴 P1 |
| C6 | banking_connector.py | N×2 requêtes import | 200 req/sync | 🔴 P1 |
| S1 | config.py | Credentials hardcodés | Sécurité | 🟠 P2 |
| S2 | main.py | Health check factice | Infra | 🟠 P2 |
| S3 | — | Pas de rate limiting | DDoS | 🟠 P2 |
| F1 | banking_tasks.py | event loop manuel | Fuites mémoire | 🟡 P3 |
| F2 | banking_connector.py | Pas de timeout HTTP | Workers bloqués | 🟡 P3 |

---

## Corrections — RFC-007

Voir `docs/refactors/RFC-007_scalability-performance/README.md` pour le détail des modifications.
