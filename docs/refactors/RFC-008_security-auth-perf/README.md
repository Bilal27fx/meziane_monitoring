# RFC-008 — Sécurité Auth + Performance (suite audit)
**Type :** refactor + bugfix
**Priorité :** CRITIQUE
**Statut :** Terminé
**Ouvert le :** 2026-03-24

---

## Problèmes corrigés

### 🔴 Celery beat — cron string invalide → tâches jamais exécutées
`celery_app.py` — `"schedule": "0 6 * * *"` ne fonctionne pas avec Celery standard.
**Fix :** `crontab(hour=6, minute=0)` sur les 3 tâches planifiées.

### 🔴 Token JWT dans `localStorage` — vulnérable XSS
`frontend/lib/api/client.ts` + `useAuth.ts` — le token était stocké dans `localStorage`,
accessible par n'importe quel script injecté.
**Fix :** Token en mémoire (module-level variable) + refresh token en `sessionStorage`.
Auto-refresh transparent avec file d'attente des requêtes concurrentes.

### 🔴 Brute force login non protégé
`auth_routes.py` — aucun rate limiting sur `/api/auth/login`.
**Fix :** Compteur Redis par email. Bloqué après 5 tentatives en 5 min (429).

### 🟠 Access token 8h → 30 min
`auth_service.py` — `ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8` trop long pour app financière.
**Fix :** 30 min. Refresh token 14 jours avec rotation.

### 🟠 Role absent du JWT → 1 requête DB par request
`utils/auth.py` — chaque endpoint authentifié faisait `db.query(User).filter(...)`.
**Fix :** `role` + `is_active` inclus dans le payload JWT. `get_current_user` lit depuis le token (0 DB). `get_current_user_db` disponible pour `/me` uniquement.

### 🟠 Refresh token sans rotation + logout passif
`auth_routes.py` — l'ancien refresh token restait valide après un refresh.
**Fix :** Rotation via blacklist Redis (`jti` unique par token). Endpoint `/api/auth/logout` révoque le refresh token côté serveur.

### 🟠 Cashflow — 3 requêtes par bien/SCI/global → 1 requête CASE
`cashflow_service.py` — `get_bien_cashflow`, `get_sci_cashflow`, `get_global_cashflow` faisaient
3 requêtes chacune (total/revenus/dépenses séparés).
**Fix :** 1 requête `CASE` chacune → 9 requêtes éliminées par appel dashboard.

### 🟠 `send_alerte_impayes_task` — N+1 queries → joinedload
`quittance_tasks.py` — pour chaque impayé : `db.query(Bail)` + `db.query(Locataire)`.
**Fix :** `joinedload(Quittance.bail).joinedload(Bail.locataire)` = 1 requête.

### 🟠 `generate_quittances_task` — N vérifications doublon → batch
`quittance_tasks.py` — 1 `SELECT` par bail pour vérifier existence.
**Fix :** 1 requête batch `IN (bail_ids)` + `db.add_all()` pour les nouvelles.

### 🟡 `detect_duplicates` — `.all()` → `.limit(1)`
`transaction_service.py` — chargeait tous les doublons alors que seule la présence est testée.
**Fix :** `.limit(1).all()` — même interface, 0 surcharge mémoire.

### 🟡 `gpt-4` → `gpt-4o-mini`
`categorization_service.py` — GPT-4 pour classifier des libellés bancaires = sur-dimensionné.
**Fix :** `gpt-4o-mini` = 100× moins cher, précision identique sur classification.

### 🟡 Tasks Celery sans `max_retries`
`quittance_tasks.py` — `generate_quittances_task` et `send_alerte_impayes_task` n'avaient pas de retry.
**Fix :** `max_retries=3` + `countdown=60*(retries+1)` sur les deux tasks.

---

## Fichiers modifiés

| Fichier | Changement |
|---------|-----------|
| `backend/app/tasks/celery_app.py` | crontab() |
| `backend/app/services/auth_service.py` | token 30min, role dans JWT, jti refresh |
| `backend/app/utils/auth.py` | CurrentUser dataclass, 0 DB par request |
| `backend/app/api/auth_routes.py` | rate limit login, rotation refresh, logout endpoint |
| `backend/app/services/cashflow_service.py` | 3× (3→1 requête CASE) |
| `backend/app/tasks/quittance_tasks.py` | joinedload, batch check, max_retries |
| `backend/app/services/transaction_service.py` | detect_duplicates .limit(1) |
| `backend/app/services/categorization_service.py` | gpt-4o-mini |
| `frontend/lib/api/client.ts` | token en mémoire, auto-refresh |
| `frontend/lib/hooks/useAuth.ts` | tokenStore, logout révocation, rate limit 429 |
