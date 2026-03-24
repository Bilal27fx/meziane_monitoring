# Suivi des évolutions — Meziane Monitoring
**Fichier de référence** — mis à jour à chaque RFC ouvert ou clôturé.

---

## Index des RFC

| ID | Titre | Type | Priorité | Statut | Date ouverture | Date clôture |
|----|-------|------|----------|--------|----------------|--------------|
| RFC-008 | Sécurité Auth + Performance suite | refactor | CRITIQUE | Terminé | 2026-03-24 | 2026-03-24 |
| RFC-007 | Scalabilité & Performance Backend | refactor | CRITIQUE | Terminé | 2026-03-24 | 2026-03-24 |
| RFC-006 | Suppression totale mock data + branchement API | refactor | CRITIQUE | Terminé | 2026-03-24 | 2026-03-24 |
| RFC-001 | Fix endpoints validate/reject | bugfix | CRITIQUE | Terminé | 2026-03-24 | 2026-03-24 |
| RFC-002 | Routes backend quittances | feature | HAUTE | Terminé | 2026-03-24 | 2026-03-24 |
| RFC-003 | Upload documents locataire | feature | MOYENNE | Terminé | 2026-03-24 | 2026-03-24 |
| RFC-004 | Boutons QuittancesPanel connectés API | bugfix | MOYENNE | Terminé | 2026-03-24 | 2026-03-24 |
| RFC-005 | Suppression mock data fallback silencieux | refactor | BASSE | Terminé | 2026-03-24 | 2026-03-24 |

---

## Légende statuts

| Statut | Signification |
|--------|---------------|
| En attente | Identifié, pas encore démarré |
| En cours | Branche active, dev en cours |
| En revue | PR ouverte, attente validation |
| Terminé | Mergé en main |
| Annulé | Abandonné avec justification |

---

## Détail des RFC

---

### RFC-001 — Fix endpoints validate/reject
**Dossier :** `refactors/RFC-001_fix-endpoints-validate-reject/`
**Type :** bugfix
**Priorité :** CRITIQUE
**Statut :** En attente
**Ouvert le :** 2026-03-24

**Problème :**
Le frontend appelle `/api/transactions/{id}/validate` et `/api/transactions/{id}/reject` (anglais).
Le backend expose `/api/transactions/{id}/valider` et `/api/transactions/{id}/rejeter` (français).
Résultat : toute validation ou rejet de transaction retourne un 404.

**Fichiers impactés :**
- `frontend/lib/hooks/useAdmin.ts` — lignes 185 et 193

**Correction :**
Remplacer `validate` → `valider` et `reject` → `rejeter` dans `useAdmin.ts`.

---

### RFC-002 — Routes backend quittances
**Dossier :** `refactors/RFC-002_quittance-routes-backend/`
**Type :** feature
**Priorité :** HAUTE
**Statut :** En attente
**Ouvert le :** 2026-03-24

**Problème :**
Le frontend appelle `GET /api/locataires/{id}/quittances` mais aucune route n'existe en backend.
Aucun fichier `quittance_routes.py` dans `backend/app/api/`.
Le modèle `Quittance` existe (`backend/app/models/quittance.py`) mais n'est pas exposé.

**Fichiers impactés :**
- `frontend/lib/hooks/useAdmin.ts` — ligne 219
- `backend/app/api/` — fichier à créer
- `backend/app/main.py` — import à ajouter

**Correction :**
Créer `backend/app/api/quittance_routes.py` avec :
- `GET /api/locataires/{locataire_id}/quittances` — liste des quittances
- `GET /api/quittances/{id}/pdf` — téléchargement PDF
- `POST /api/locataires/{locataire_id}/quittances/generer` — génération + email
Enregistrer le router dans `main.py`.

---

### RFC-003 — Upload documents locataire
**Dossier :** `refactors/RFC-003_upload-documents-locataire/`
**Type :** feature
**Priorité :** MOYENNE
**Statut :** En attente
**Ouvert le :** 2026-03-24

**Problème :**
Dans `LocataireForm.tsx`, la zone drag-and-drop "Glisser-déposer les documents" est purement décorative.
Aucun `<input type="file">`, aucun handler `onChange`, aucun appel API.
Le backend a pourtant un endpoint complet : `POST /api/documents/upload-locataire`.

**Fichiers impactés :**
- `frontend/components/admin/forms/LocataireForm.tsx` — lignes 249-255

**Correction :**
- Ajouter un `<input type="file" multiple accept=".pdf,.jpg,.png">` caché
- Ajouter un état `selectedFiles` + handler `onFileChange`
- Ajouter un select `type_document` (TypeDocument enum)
- Appeler `POST /api/documents/upload-locataire` via `FormData`
- Afficher la liste des fichiers sélectionnés avant envoi

---

### RFC-004 — Boutons QuittancesPanel connectés API
**Dossier :** `refactors/RFC-004_quittances-panel-api/`
**Type :** bugfix
**Priorité :** MOYENNE
**Statut :** En attente
**Ouvert le :** 2026-03-24

**Problème :**
Dans `QuittancesPanel.tsx` :
- `handleDownload(mois)` → affiche un toast "téléchargée" sans appel API
- `handleGenerate()` → affiche un toast "générée et envoyée par email" sans appel API

**Dépend de :** RFC-002 (les routes backend doivent exister)

**Fichiers impactés :**
- `frontend/components/admin/panels/QuittancesPanel.tsx` — lignes 34-40

**Correction :**
- `handleDownload` → appel `GET /api/quittances/{id}/pdf` + `window.open(url)`
- `handleGenerate` → appel `POST /api/locataires/{id}/quittances/generer` via mutation

---

### RFC-005 — Suppression mock data fallback silencieux
**Dossier :** `refactors/RFC-005_mock-data-fallback/`
**Type :** refactor
**Priorité :** BASSE
**Statut :** En attente
**Ouvert le :** 2026-03-24

**Problème :**
Dans `useAdmin.ts`, tous les hooks de lecture ont un catch silencieux qui retourne des données mock sans notifier l'utilisateur :
```ts
} catch {
  return { items: MOCK_SCIS, ... }  // l'user ne voit aucune erreur
}
```
Hooks concernés : `useSCIs`, `useBiens`, `useLocataires`, `useTransactions`, `useQuittances`.

**Fichiers impactés :**
- `frontend/lib/hooks/useAdmin.ts` — lignes 45-227

**Correction :**
- Supprimer les blocs `catch` qui retournent des mocks
- Laisser React Query gérer l'état `isError` nativement
- Afficher un `toast.error` dans le `onError` de la query si besoin
- Supprimer les constantes `MOCK_*` devenues inutiles

---

## Journal des clôtures

| Date | RFC | Résumé des changements |
|------|-----|------------------------|
| 2026-03-24 | RFC-008 | Celery crontab, token mémoire+sessionStorage, rate limit login Redis, JWT 30min+role, get_current_user 0 DB, refresh rotation+blacklist, logout endpoint, cashflow 3→1 requête×3, quittances joinedload+batch, detect_duplicates limit(1), gpt-4o-mini, max_retries tasks |
| 2026-03-24 | RFC-007 | Index DB (14 index), pool_size=20, dashboard KPI -2 requêtes, cashflow 30j GROUP BY SQL, top biens ORDER BY SQL, timeouts httpx, asyncio.run(), health check réel |
| 2026-03-24 | RFC-001 | `useAdmin.ts` — `/validate` → `/valider`, `/reject` → `/rejeter` |
| 2026-03-24 | RFC-002 | `quittance_routes.py` + `quittance_schema.py` créés, router enregistré dans `main.py` |
| 2026-03-24 | RFC-003 | `LocataireForm.tsx` — input file + handler + upload `FormData` vers `/api/documents/upload-locataire` |
| 2026-03-24 | RFC-004 | `QuittancesPanel.tsx` — `handleDownload` appelle PDF, `handleGenerate` appelle mutation, `useGenerateQuittance` ajouté dans `useAdmin.ts` |
| 2026-03-24 | RFC-005 | `useAdmin.ts` — suppression MOCK_*, catch silencieux, import toast inutilisé |
| 2026-03-24 | RFC-006 | Suppression complète de tous les MOCK data : `useDashboard.ts`, `useAgent.ts`, 5 composants dashboard (DEFAULT_DATA), `OpportunitesWidget`, `LocatairesCards`. `dashboard/page.tsx` branché sur `useFullDashboard()` — KPIs, charts, tableaux tous en données réelles |
