# RFC-007 — Scalabilité & Performance Backend
**Type :** refactor
**Priorité :** CRITIQUE
**Statut :** En cours
**Ouvert le :** 2026-03-24
**Branche :** update&optimisation

---

## Problème

L'audit GitNexus a identifié 6 blocages critiques qui empêchent le passage à l'échelle.
Voir `docs/architecture/SCALABILITY_AUDIT.md` pour l'analyse complète.

---

## Modifications

### 1. Index DB — nouvelle migration Alembic
**Fichier créé :** `backend/alembic/versions/c7d8e9f0a1b2_add_performance_indexes.py`

Index ajoutés :
- `ix_transaction_date` sur `transactions.date`
- `ix_transaction_sci_id` sur `transactions.sci_id`
- `ix_transaction_bien_id` sur `transactions.bien_id`
- `ix_bail_statut` sur `bails.statut`
- `ix_quittance_statut` sur `quittances.statut`
- `ix_quittance_bail_id` sur `quittances.bail_id`
- `ix_opportunite_statut` sur `opportunites.statut`

---

### 2. Connection pool configuré
**Fichier modifié :** `backend/app/utils/db.py`

- `pool_size=20` — connexions permanentes
- `max_overflow=40` — burst capacity
- `pool_pre_ping=True` — détecte les connexions mortes
- `echo` désactivé (log séparé)

---

### 3. Dashboard KPI — requêtes fusionnées
**Fichier modifié :** `backend/app/services/dashboard_service.py`

- `_calculate_patrimoine_net()` appelé 1 seule fois dans `get_kpi()` (suppression doublon dans `_calculate_performance_ytd`)
- `_count_alertes()` fusionné en 1 requête `UNION ALL` au lieu de 2
- `_calculate_taux_occupation()` fusionné en 1 requête `CASE` au lieu de 2
- `get_cashflow_30days()` remplacé par `GROUP BY` SQL au lieu d'agrégation Python

---

### 4. `get_top_biens_by_rentabilite()` — tri SQL
**Fichier modifié :** `backend/app/services/dashboard_service.py`

- Suppression du `.all()` sur tous les biens
- Tri `ORDER BY rentabilite_nette DESC LIMIT n` via sous-requête SQL

---

### 5. Banking connector — timeouts + asyncio.run
**Fichiers modifiés :**
- `backend/app/connectors/banking_connector.py` — `timeout=30.0` sur tous les `AsyncClient()`
- `backend/app/tasks/banking_tasks.py` — `asyncio.run()` remplace le `new_event_loop()` manuel

---

### 6. Health check réel
**Fichier modifié :** `backend/app/main.py`

- `/health` teste réellement la connexion DB avec `db.execute(text("SELECT 1"))`
- Retourne `503` si DB down

---

## Fichiers modifiés

| Fichier | Type de changement |
|---------|-------------------|
| `backend/alembic/versions/c7d8e9f0a1b2_add_performance_indexes.py` | Créé |
| `backend/app/utils/db.py` | Modifié — pool config |
| `backend/app/services/dashboard_service.py` | Modifié — requêtes optimisées |
| `backend/app/connectors/banking_connector.py` | Modifié — timeouts HTTP |
| `backend/app/tasks/banking_tasks.py` | Modifié — asyncio.run |
| `backend/app/main.py` | Modifié — vrai health check |

---

## Tests de validation

- [ ] `GET /api/dashboard/kpi` répond en < 200ms avec 10k transactions
- [ ] `GET /api/dashboard/full` répond en < 500ms
- [ ] `GET /health` retourne 503 si PostgreSQL est arrêté
- [ ] `sync_banking_task` importe 100 transactions sans error
- [ ] Pool ne sature pas avec 50 requêtes simultanées
