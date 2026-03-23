# Plan Backend Readiness — Avant attaque Frontend
**Date :** 2026-03-23
**Objectif :** Identifier et corriger tous les problèmes backend bloquants avant de démarrer le frontend Next.js 14, et poser les bases d'un système plugin multi-business.

---

## Résumé exécutif

Après analyse complète des ~70 fichiers du backend, **6 problèmes critiques bloquent le frontend** et **8 problèmes majeurs** dégradent performance et maintenabilité. Tout doit être corrigé avant d'écrire une seule ligne de React.

---

## 🔴 CRITIQUES — Bloquent le frontend

### C1 — Pas d'authentification (zéro sécurité)
**Fichier :** `config.py:47`, `main.py`
**Problème :** `SECRET_KEY` existe dans la config mais n'est jamais utilisé. Aucun endpoint de login/logout. Aucun middleware JWT. N'importe qui peut appeler n'importe quel endpoint sans s'identifier.
**Impact frontend :** Impossible de créer une page de login, impossible de protéger les routes, impossible de contextualiser les données par utilisateur.

**Ce qui manque :**
- Modèle `User` (email, hashed_password, role)
- Migration Alembic pour la table `users`
- `AuthService` avec `create_user()`, `authenticate()`, `create_token()`
- Dépendance FastAPI `get_current_user` via JWT (python-jose déjà installé)
- Routes `/api/auth/login`, `/api/auth/refresh`, `/api/auth/me`
- Middleware qui protège toutes les routes sauf `/`, `/health`, `/api/auth/login`

---

### C2 — Pas de pagination sur la majorité des routes
**Fichiers :** `bien_routes.py:26`, `sci_routes.py`, `locataire_routes.py`, `opportunite_routes.py`
**Problème :** `GET /api/biens/`, `GET /api/sci/`, `GET /api/locataires/` retournent **tous** les enregistrements sans limit/offset. Seul `transaction_routes.py` a une pagination.
**Impact frontend :** Un tableau avec 1000 biens fait crasher le navigateur. Impossible de faire un infinite scroll ou une pagination correcte.

**Correction :** Ajouter `limit: int = Query(50)` et `offset: int = Query(0)` + retourner un objet `{ data: [...], total: int, page: int }` sur toutes les routes de liste.

---

### C3 — Endpoint `/api/dashboard/full` trop lent (N+1 massif)
**Fichier :** `dashboard_service.py`
**Problème principal — `get_locataires_overview()`** (lignes 326–374) : pour chaque locataire, fait **3 requêtes SQL séparées** (bail actif, dernière quittance, nb impayés). Avec 20 locataires = 60 requêtes.
**Problème secondaire — `get_top_biens_by_rentabilite()`** (lignes 247–282) : fetche tous les biens puis appelle `get_bien_rentabilite()` pour chacun = N×2 requêtes.
**Problème tertiaire — `get_sci_overview()`** (lignes 286–320) : boucle sur les SCI avec 3 requêtes séparées par SCI.

**Impact frontend :** Le dashboard principal se charge en 3-8 secondes à vide. Avec des données réelles, c'est inutilisable.

**Correction :** Réécrire avec des JOINs SQLAlchemy + `joinedload()`, ou des sous-requêtes agrégées en une seule passe.

---

### C4 — cashflow mensuel = 12 requêtes SQL séparées
**Fichier :** `cashflow_service.py:85-94, 148-157, 197-206`
**Problème :** Les 3 méthodes `get_*_cashflow_mensuel()` font une boucle `for mois in range(1, 13)` qui appelle `get_*_cashflow()` à chaque itération = **12 requêtes SQL** au lieu d'une.

**Correction :**
```python
# Remplacer par une seule requête GROUP BY :
self.db.query(
    extract('month', Transaction.date).label('mois'),
    func.sum(case((Transaction.montant > 0, Transaction.montant), else_=0)).label('revenus'),
    func.sum(case((Transaction.montant < 0, Transaction.montant), else_=0)).label('depenses'),
).filter(extract('year', Transaction.date) == annee).group_by('mois').all()
```

---

### C5 — CORS hardcodé pour localhost uniquement
**Fichier :** `main.py:44-51`
**Problème :** `allow_origins=["http://localhost:3000"]`. En production (Vercel, Netlify, domaine custom), le frontend sera bloqué par CORS.
**Correction :** Lire les origines autorisées depuis `settings.ALLOWED_ORIGINS` (liste configurable via `.env`).

---

### C6 — Aucun schéma de réponse sur les endpoints analytics
**Fichier :** `transaction_routes.py:157-174`
**Problème :** `GET /analytics/by-categorie` et `GET /analytics/mensuel/{sci_id}/{annee}` n'ont pas de `response_model`. FastAPI retourne un dict non typé — le frontend TypeScript ne peut pas générer des types automatiquement depuis OpenAPI.
**Correction :** Créer des schemas Pydantic `AnalyticsCategorieResponse` et `AnalyticsMensuelResponse`.

---

## 🟠 MAJEURS — Dégradent qualité et maintenabilité

### M1 — `Transaction.created_at` utilise `Date` au lieu de `DateTime`
**Fichier :** `transaction.py:69`
```python
created_at = Column(Date, nullable=False, default=datetime.utcnow)
# ^^^^^ Date perd l'heure → trier par created_at donne des résultats imprévisibles
```
**Correction :** `Column(DateTime, nullable=False, default=datetime.utcnow)`
Migration Alembic nécessaire.

---

### M2 — `get_patrimoine_12months()` retourne la même valeur pour tous les mois
**Fichier :** `dashboard_service.py:199-215`
**Problème :** Le graph "évolution patrimoine 12 mois" est **complètement faux** — c'est un plateau horizontal. Il n'y a pas d'historique des valeurs.
**Plan :**
- Option A (rapide) : créer une table `HistoriquePatrimoine(date, sci_id, valeur)` alimentée par un job mensuel Celery.
- Option B (immédiat) : calculer l'évolution en se basant sur les transactions cumulées mois par mois depuis `date_acquisition`.

---

### M3 — `Opportunite.risques` stocké comme JSON string
**Fichier :** `agent_prospection.py:254`
```python
risques=json.dumps(scoring.get("risques", []))
# Stocké comme TEXT → impossible à filtrer/indexer en SQL
```
**Correction :** Utiliser `Column(JSON)` dans le modèle SQLAlchemy.
Migration Alembic nécessaire.

---

### M4 — `BankingConnectorService` utilise `requests` (synchrone)
**Fichier :** `banking_connector.py:1-224`
**Problème :** `requests` est synchrone et bloque le thread uvicorn. `httpx` est déjà dans requirements.
**Correction :** Convertir en `async def` avec `httpx.AsyncClient`.

---

### M5 — Pas de gestion centralisée des erreurs
**Problème :** Chaque route fait son propre `try/except` avec des messages d'erreur inconsistants. Le frontend doit gérer des formats d'erreur différents.
**Correction :** Ajouter un `@app.exception_handler(Exception)` global dans `main.py` + une classe `APIError` standardisée.

---

### M6 — `config.py` chemin `.env` relatif fragile
**Fichier :** `config.py:65`
```python
env_file = "../.env"
# Fonctionne seulement si lancé depuis backend/
```
**Correction :** Utiliser `Path(__file__).parent.parent / ".env"` pour un chemin absolu fiable.

---

### M7 — Pas de Celery tasks implémentées
**Fichier :** `backend/app/tasks/__init__.py` (vide)
**Problème :** Redis est configuré, Celery est dans les requirements, mais aucune task n'existe. L'agent prospection et la sync bancaire tournent en synchrone dans la requête HTTP — ça timeout.
**Tâches à implémenter :**
- `sync_banking_task(sci_id, account_id)` — déclenché par webhook Bridge
- `run_prospection_agent_task()` — job quotidien 6h
- `generate_quittances_task(mois, annee)` — job mensuel 1er du mois
- `send_alerte_impayes_task()` — job hebdomadaire

---

### M8 — `BienResponse` et `LocalataireResponse` sans champs enrichis
**Fichiers :** `bien_schema.py:63-67`, `locataire_schema.py`
**Problème :** La réponse d'un bien ne contient pas `sci_nom`, ni les locataires associés, ni le cashflow. Le frontend devra faire N requêtes supplémentaires.
**Correction :** Créer des schemas `BienDetailResponse` avec `sci_nom`, `bail_actif`, `cashflow_ytd` pour les cas où le frontend a besoin du détail.

---

## 🟡 SYSTÈME PLUGIN MULTI-BUSINESS

### Architecture proposée

L'objectif est de supporter plusieurs "business" (immobilier France, centre commercial Algérie, futurs modules) sans toucher au code core.

```
backend/
├── app/
│   ├── core/                    ← Code partagé (auth, db, config, logger)
│   ├── plugins/                 ← Système plugin
│   │   ├── __init__.py          ← PluginRegistry
│   │   ├── base.py              ← BusinessModule (classe abstraite)
│   │   ├── immobilier/          ← Plugin immobilier France (code actuel)
│   │   │   ├── __init__.py      ← ImmobilierPlugin(BusinessModule)
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   ├── api/
│   │   │   └── agents/
│   │   └── commercial_algerie/  ← Plugin futur
│   │       ├── __init__.py      ← CommercialAlgeriePlugin(BusinessModule)
│   │       ├── models/          ← Boutique, BailCommercial, etc.
│   │       ├── schemas/
│   │       ├── services/
│   │       └── api/
│   └── main.py                  ← Charge les plugins dynamiquement
```

### Interface `BusinessModule` (base.py)

```python
from abc import ABC, abstractmethod
from fastapi import FastAPI

class BusinessModule(ABC):
    name: str           # "immobilier" | "commercial_algerie"
    version: str        # "1.0.0"
    api_prefix: str     # "/api/immobilier" | "/api/commercial"

    @abstractmethod
    def register_routes(self, app: FastAPI) -> None:
        """Monte les routes APIRouter sur l'application FastAPI"""
        pass

    @abstractmethod
    def get_dashboard_kpi(self, db) -> dict:
        """Retourne les KPI pour ce business (affiché dans le dashboard global)"""
        pass

    def on_startup(self) -> None:
        """Hook optionnel exécuté au démarrage du serveur"""
        pass
```

### `PluginRegistry` (`plugins/__init__.py`)

```python
class PluginRegistry:
    _plugins: dict[str, BusinessModule] = {}

    @classmethod
    def register(cls, plugin: BusinessModule):
        cls._plugins[plugin.name] = plugin

    @classmethod
    def load_all(cls, app: FastAPI):
        for plugin in cls._plugins.values():
            plugin.register_routes(app)
            plugin.on_startup()

    @classmethod
    def get_all_kpis(cls, db) -> dict:
        return {name: p.get_dashboard_kpi(db) for name, p in cls._plugins.items()}
```

### `main.py` avec plugins

```python
from app.plugins import PluginRegistry
from app.plugins.immobilier import ImmobilierPlugin

# Enregistre les plugins actifs
PluginRegistry.register(ImmobilierPlugin())
# PluginRegistry.register(CommercialAlgeriePlugin())  # Décommenter quand prêt

# Monte toutes les routes
PluginRegistry.load_all(app)
```

### Endpoint dashboard unifié

```
GET /api/dashboard/global
→ Agrège les KPI de tous les plugins enregistrés
→ { "immobilier": {...}, "commercial_algerie": {...} }
```

---

## Plan d'exécution par ordre de priorité

### Sprint 1 — Sécurité & Fondations (avant tout le reste)
| # | Tâche | Fichiers impactés | Effort |
|---|-------|-------------------|--------|
| 1 | Ajouter modèle `User` + migration | `models/user.py` (nouveau) | 1h |
| 2 | Implémenter `AuthService` + JWT | `services/auth_service.py` (nouveau) | 2h |
| 3 | Routes `/api/auth/*` | `api/auth_routes.py` (nouveau) | 1h |
| 4 | Dépendance `get_current_user` | `utils/auth.py` (nouveau) | 30min |
| 5 | Protéger toutes les routes existantes | Tous les `*_routes.py` | 1h |
| 6 | CORS depuis `.env` | `main.py` | 15min |
| 7 | Fix chemin `.env` | `config.py` | 5min |

### Sprint 2 — Performance & Correction données
| # | Tâche | Fichiers impactés | Effort |
|---|-------|-------------------|--------|
| 8 | Réécrire cashflow mensuel (GROUP BY) | `cashflow_service.py` | 1h |
| 9 | Corriger N+1 dans dashboard_service | `dashboard_service.py` | 2h |
| 10 | Pagination sur toutes les routes liste | Tous les `*_routes.py` | 1h |
| 11 | Schemas response_model analytics | `transaction_routes.py` + schemas | 30min |
| 12 | Fix `Transaction.created_at` → DateTime | `models/transaction.py` + migration | 30min |
| 13 | Fix `Opportunite.risques` → JSON column | `models/opportunite.py` + migration | 30min |
| 14 | Gestion erreurs centralisée | `main.py` | 30min |

### Sprint 3 — Async & Background jobs
| # | Tâche | Fichiers impactés | Effort |
|---|-------|-------------------|--------|
| 15 | Convertir BankingConnector en async | `connectors/banking_connector.py` | 2h |
| 16 | Setup Celery app + worker | `tasks/celery_app.py` (nouveau) | 1h |
| 17 | Task `sync_banking_task` | `tasks/banking_tasks.py` (nouveau) | 1h |
| 18 | Task `run_prospection_agent_task` | `tasks/agent_tasks.py` (nouveau) | 1h |
| 19 | Task `generate_quittances_task` | `tasks/quittance_tasks.py` (nouveau) | 1h |

### Sprint 4 — Système Plugin
| # | Tâche | Fichiers impactés | Effort |
|---|-------|-------------------|--------|
| 20 | Créer `BusinessModule` base | `plugins/base.py` (nouveau) | 30min |
| 21 | Créer `PluginRegistry` | `plugins/__init__.py` (nouveau) | 30min |
| 22 | Migrer code actuel → `ImmobilierPlugin` | Réorganisation dossiers | 3h |
| 23 | Adapter `main.py` pour charger plugins | `main.py` | 30min |
| 24 | Endpoint dashboard global multi-plugin | `api/dashboard_routes.py` | 1h |

### Sprint 5 — Enrichissement schemas (pour le frontend)
| # | Tâche | Fichiers impactés | Effort |
|---|-------|-------------------|--------|
| 25 | `BienDetailResponse` avec sci_nom, bail_actif | `schemas/bien_schema.py` | 30min |
| 26 | `LocataireDetailResponse` avec bail + quittances | `schemas/locataire_schema.py` | 30min |
| 27 | Fix `get_patrimoine_12months()` avec données réelles | `dashboard_service.py` | 2h |

---

## Ce que le frontend peut attaquer APRÈS ces sprints

Une fois les 5 sprints terminés, le frontend aura :
- Une API sécurisée avec JWT → pages login/logout/me
- Des endpoints paginés → tableaux infinis sans crash
- Un dashboard qui charge en < 500ms → expérience fluide
- Des types OpenAPI complets → génération automatique types TypeScript
- Un système plugin → routing frontend par module business
- Des background jobs → notifications temps réel via WebSocket ou polling

---

## Métriques de qualité cibles

| Métrique | Aujourd'hui | Cible |
|----------|-------------|-------|
| Temps chargement dashboard /full | ~3-8s | < 500ms |
| Endpoints avec auth | 0% | 100% |
| Endpoints avec pagination | 10% | 100% |
| Endpoints avec response_model | 80% | 100% |
| Coverage tests | 0% | 60% minimum |
| Requêtes SQL pour cashflow mensuel | 12 | 1 |
| N+1 dans dashboard | ~40 queries | ~5 queries |

---

*Généré par analyse statique complète du code — 2026-03-23*
