# Plan général — Meziane Monitoring
**Mis à jour :** 2026-03-24
**Branche active :** `update&optimisation`

---

## Vue d'ensemble

Le backend est production-ready (5 sprints terminés). Le frontend est construit mais plusieurs points de connexion avec l'API sont cassés ou non implémentés. Ce plan couvre les corrections à apporter pour avoir une application pleinement fonctionnelle.

---

## Phase en cours — Corrections & Connexions API

### Statut
```
RFC-001  Fix endpoints validate/reject        [ ] En attente
RFC-002  Routes backend quittances            [ ] En attente
RFC-003  Upload documents locataire           [ ] En attente
RFC-004  Boutons QuittancesPanel → API        [ ] En attente
RFC-005  Suppression mock data fallback       [ ] En attente
```

### Priorité d'exécution

| Ordre | RFC | Raison |
|-------|-----|--------|
| 1 | RFC-001 | CRITIQUE — 404 garanti sur valider/rejeter transaction |
| 2 | RFC-002 | HAUTE — quittances inexistantes en backend |
| 3 | RFC-003 | MOYENNE — upload docs UI non fonctionnel |
| 4 | RFC-004 | MOYENNE — boutons quittances ne font rien |
| 5 | RFC-005 | BASSE — erreurs API masquées silencieusement |

---

## Historique des phases terminées

| Phase | Description | Fichier |
|-------|-------------|---------|
| Backend Readiness (5 sprints) | Auth, performance, async, plugins, schemas | `history/PROGRESSION_BACKEND_READINESS.md` |
| Frontend Build (5 phases) | Foundation, Dashboard, Agent, Admin, Polish | `history/PROGRESSION_FRONTEND.md` |
| Plan initial backend | Analyse complète ~70 fichiers | `history/PLAN_BACKEND_READINESS.md` |
| Plan UI CRUD | SCI / Biens / Locataires | `history/PLAN_UI_CRUD_SCI_BIEN_LOCATAIRE.md` |

---

## Architecture

- Système → `architecture/ARCHITECTURE_SYSTEME.md`
- Frontend → `architecture/FRONTEND_ARCHITECTURE.md`
- Dashboard layout → `architecture/DASHBOARD_LAYOUT_PLAN.md`
- Profil & objectifs → `architecture/PROFIL_ET_OBJECTIFS.md`

---

## Suivi des RFC

Voir `TRACKING.md` pour l'état détaillé de chaque refactor.
