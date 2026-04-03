# Plan général - Meziane Monitoring
**Mis à jour :** 2026-03-25

## Vue d'ensemble

Le socle principal du projet est en place:
- backend FastAPI structuré
- frontend Next.js branché sur l'API
- auth, dashboard, documents, quittances et jobs asynchrones déjà présents

Le plan n'est plus centré sur les RFC 001 à 005: elles sont déjà terminées et tracées dans `TRACKING.md`.

## Phase actuelle

La phase active est désormais une phase de stabilisation continue:
- amélioration de la qualité documentaire
- alignement doc / code / architecture
- durcissement progressif de l'auth, des flux critiques et de la maintenabilité
- ouverture de nouvelles RFC au fil des besoins réels

## Etat des travaux RFC connus

RFC terminées à date:
- RFC-001 - Fix endpoints validate/reject
- RFC-002 - Routes backend quittances
- RFC-003 - Upload documents locataire
- RFC-004 - Boutons QuittancesPanel connectés API
- RFC-005 - Suppression mock data fallback silencieux
- RFC-006 - Suppression totale mock data + branchement API
- RFC-007 - Scalabilité & Performance Backend
- RFC-008 - Sécurité Auth + Performance suite

Le détail et le journal des clôtures sont dans `TRACKING.md`.

## Priorités permanentes

Tant qu'aucune nouvelle RFC n'est ouverte, les priorités structurantes restent:
- garder la documentation à jour
- préserver la cohérence entre frontend, backend et architecture
- documenter chaque refactor important
- analyser l'impact avant modification via GitNexus

## Historique utile

| Sujet | Fichier |
|-------|---------|
| Backend readiness | `history/PROGRESSION_BACKEND_READINESS.md` |
| Construction frontend | `history/PROGRESSION_FRONTEND.md` |
| Plan initial backend | `history/PLAN_BACKEND_READINESS.md` |
| Plan UI CRUD | `history/PLAN_UI_CRUD_SCI_BIEN_LOCATAIRE.md` |

## Architecture

- Système: `architecture/ARCHITECTURE_SYSTEME.md`
- Frontend: `architecture/FRONTEND_ARCHITECTURE.md`
- Dashboard: `architecture/DASHBOARD_LAYOUT_PLAN.md`
- Profil et objectifs: `architecture/PROFIL_ET_OBJECTIFS.md`

## Suivi des RFC

Voir `TRACKING.md` pour:
- l'état détaillé des RFC
- les clôtures
- le résumé des changements déjà livrés
