# Plan — Connexion UI CRUD Complet : SCI / Bien / Locataire

> Objectif : brancher le frontend existant sur le backend réel.
> Tous les composants Tab + Form existent déjà côté UI. Ce plan liste uniquement les **fichiers à modifier** et les **désalignements à corriger**.

---

## État actuel

| Entité | Tab UI | Form UI | Hooks | Backend endpoint | Branché ? |
|--------|--------|---------|-------|-----------------|-----------|
| SCI | ✅ SCITab | ✅ SCIForm | ✅ useSCIs… | ✅ /api/sci | ⚠️ Champs désalignés |
| Bien | ✅ BiensTab | ✅ BienForm | ✅ useBiens… | ✅ /api/biens | ⚠️ Champs désalignés |
| Locataire | ✅ LocatairesTab | ✅ LocataireForm | ✅ useLocataires… | ✅ /api/locataires | ⚠️ Champs désalignés + bail manquant |

Les hooks tombent sur les mocks quand le backend échoue. Il faut aligner les contrats de données pour que les vrais appels fonctionnent.

---

## Problèmes identifiés par entité

### 1. Format de réponse API (global)

**Problème** : Le backend retourne `List[T]` directement, le frontend attend `PaginatedResponse<T>` soit `{ items, total, page, per_page, pages }`.

**Fichiers concernés** :
- `backend/app/api/sci_routes.py` — `get_all_sci()`
- `backend/app/api/bien_routes.py` — `get_all_biens()`
- `backend/app/api/locataire_routes.py` — `get_all_locataires()`

**Correction** : Wrapper la réponse dans un objet paginé OU adapter les hooks pour accepter `List[T]` directement.

> **Choix recommandé** : Adapter les hooks frontend (plus rapide, moins de risques backend).

---

### 2. SCI — Désalignement des champs

| Frontend (`SCIFormData`) | Backend (`SCICreate`) | Action |
|--------------------------|-----------------------|--------|
| `capital_social` | `capital` | Renommer dans form/type |
| `adresse_siege` | `siege_social` | Renommer dans form/type |
| `email` | ❌ absent | Supprimer du form ou ajouter au schema |
| ❌ absent | `gerant_nom` | Ajouter au form |
| ❌ absent | `gerant_prenom` | Ajouter au form |
| `siret` (libre) | `siret` (exactement 14 chars) | Ajouter validation |

**`SCIResponse` manque** : `nb_biens`, `valeur_totale`, `cashflow_mensuel`
→ Ces champs sont affichés dans `SCITab` mais pas retournés par le backend.
→ À ajouter dans `SCIResponse` + calculés dans `PatrimoineService`.

**Fichiers à modifier** :
```
frontend/lib/types/index.ts          → interface SCI + SCIFormData
frontend/components/admin/forms/SCIForm.tsx  → renommer champs + ajouter gérant
backend/app/schemas/sci_schema.py    → ajouter nb_biens, valeur_totale, cashflow_mensuel dans SCIResponse
backend/app/services/patrimoine_service.py  → calculer ces 3 champs dans get_all_sci()
```

---

### 3. Bien — Désalignement des champs

| Frontend (`BienFormData`) | Backend (`BienCreate`) | Action |
|---------------------------|------------------------|--------|
| `type` | `type_bien` | Renommer |
| `complement` | `complement_adresse` | Renommer |
| `dpe` | `dpe_classe` | Renommer |
| `validite_dpe` | `dpe_date_validite` | Renommer |

**Types de bien** :
- Frontend : `appartement, maison, bureau, commerce, terrain, parking`
- Backend (`TypeBien`) : `appartement, studio, maison, local_commercial, immeuble, parking, autre`
- → Aligner les valeurs (supprimer `bureau`, `commerce`, `terrain` ; ajouter `studio`, `local_commercial`, `immeuble`, `autre`)

**Champs calculés manquants dans `BienResponse`** : `loyer_mensuel`, `tri_net`
→ Ces champs sont calculés depuis le bail actif.
→ À ajouter dans `BienResponse` + calculés dans `PatrimoineService`.

**Filtre `statut` absent dans le backend** :
→ Ajouter `statut: Optional[StatutBien] = Query(None)` dans `get_all_biens()`.

**Fichiers à modifier** :
```
frontend/lib/types/index.ts                    → interface Bien + BienFormData + BienParams
frontend/components/admin/forms/BienForm.tsx   → renommer champs + corriger types de bien
frontend/lib/hooks/useAdmin.ts                 → adapter mapping champs envoyés
backend/app/schemas/bien_schema.py             → ajouter loyer_mensuel + tri_net dans BienResponse
backend/app/api/bien_routes.py                 → ajouter filtre statut
backend/app/services/patrimoine_service.py     → calculer loyer_mensuel + tri_net
```

---

### 4. Locataire — Désalignement + bail manquant

#### 4a. Champs requis côté backend stricts

`LocataireCreate` rend **obligatoires** : `telephone`, `date_naissance`, `profession`, `revenus_annuels`
→ Le frontend les a en optionnel → les validations form doivent être alignées
→ OU rendre ces champs optionnels dans `LocataireCreate` (recommandé)

#### 4b. `LocataireResponse` incomplet

Le frontend attend :
```ts
{
  bien_id, bien,            // ← absent dans LocataireResponse
  bail,                     // ← absent (objet Bail)
  statut_paiement,          // ← absent
  jours_retard              // ← absent
}
```

→ À ajouter dans `LocataireResponse` ou créer `LocataireDetailResponse` et l'utiliser dans le GET list.

#### 4c. Bail — aucun endpoint dédié

Le `LocataireForm` collecte des données de bail (`date_debut`, `date_fin`, `loyer`, `charges`, `depot_garantie`, `type_revision`) mais le backend n'a pas d'endpoint de création de bail.

**Option A** : Intégrer la création du bail dans `POST /api/locataires/`
→ `LocataireCreate` accepte des données bail optionnelles → service crée bail en même temps.

**Option B** : Créer un endpoint `/api/bails/` dédié
→ Après création locataire, appel séparé pour le bail.

> **Choix recommandé** : Option A (un seul appel, plus simple côté UI).

**Fichiers à modifier** :
```
backend/app/schemas/locataire_schema.py  → rendre champs optionnels + ajouter BailData dans LocataireCreate + enrichir LocataireResponse
backend/app/models/locataire.py          → vérifier relation bail
backend/app/services/patrimoine_service.py → create_locataire() gère bail + calcule statut_paiement
frontend/lib/types/index.ts              → interface Locataire + LocataireFormData
frontend/components/admin/forms/LocataireForm.tsx  → aligner avec nouveaux champs
frontend/lib/hooks/useAdmin.ts           → adapter payload envoyé
```

---

## Plan d'exécution (ordre recommandé)

### Étape 1 — Backend : Aligner les schemas de réponse (wrapping + champs calculés)

**Priorité haute** — sans ça, les hooks frontend ne peuvent pas parser les données.

- [ ] `sci_routes.py` + `sci_schema.py` : wrapper réponse en `{ items, total }` + ajouter `nb_biens`, `valeur_totale`, `cashflow_mensuel`
- [ ] `bien_routes.py` + `bien_schema.py` : wrapper + ajouter `loyer_mensuel`, `tri_net` + filtre statut
- [ ] `locataire_routes.py` + `locataire_schema.py` : wrapper + enrichir réponse avec bail + statut_paiement

### Étape 2 — Backend : Aligner les schemas de création

- [ ] `sci_schema.py` : corriger noms de champs (`capital`, `siege_social`)
- [ ] `bien_schema.py` : corriger noms de champs (`type_bien`, `complement_adresse`, `dpe_classe`, `dpe_date_validite`)
- [ ] `locataire_schema.py` : rendre champs optionnels + intégrer bail dans `LocataireCreate`

### Étape 3 — Backend : Enrichir `patrimoine_service.py`

- [ ] `get_all_sci()` : calculer `nb_biens`, `valeur_totale`, `cashflow_mensuel` par SCI
- [ ] `get_all_biens()` : calculer `loyer_mensuel` et `tri_net` depuis bail actif
- [ ] `get_all_locataires()` : inclure bail actif + calculer `statut_paiement` / `jours_retard`
- [ ] `create_locataire()` : créer bail si données bail fournies

### Étape 4 — Frontend : Aligner les types TypeScript

- [ ] `lib/types/index.ts` : mettre à jour `SCI`, `SCIFormData`, `Bien`, `BienFormData`, `Locataire`, `LocataireFormData`

### Étape 5 — Frontend : Adapter les hooks

- [ ] `lib/hooks/useAdmin.ts` :
  - Adapter parsers de réponse (`response.data` → `response.data` si liste ou wrapper selon choix)
  - Corriger les noms de champs dans les payloads mutate

### Étape 6 — Frontend : Corriger les formulaires

- [ ] `SCIForm.tsx` : renommer `capital_social`→`capital`, `adresse_siege`→`siege_social`, ajouter `gerant_nom`/`gerant_prenom`, supprimer `email` ou l'ajouter au backend
- [ ] `BienForm.tsx` : renommer `type`→`type_bien`, `complement`→`complement_adresse`, `dpe`→`dpe_classe`, `validite_dpe`→`dpe_date_validite`, corriger enum types de bien
- [ ] `LocataireForm.tsx` : aligner avec champs optionnels, vérifier section bail

---

## Récapitulatif des fichiers à toucher

### Backend
| Fichier | Modifications |
|---------|--------------|
| `backend/app/schemas/sci_schema.py` | Champs calculés dans SCIResponse, corriger noms |
| `backend/app/schemas/bien_schema.py` | Champs calculés dans BienResponse |
| `backend/app/schemas/locataire_schema.py` | Réponse enrichie, créa bail intégrée, champs optionnels |
| `backend/app/api/sci_routes.py` | Wrapper réponse paginée |
| `backend/app/api/bien_routes.py` | Wrapper réponse paginée + filtre statut |
| `backend/app/api/locataire_routes.py` | Wrapper réponse paginée |
| `backend/app/services/patrimoine_service.py` | Calculs loyer/tri_net/cashflow + création bail |

### Frontend
| Fichier | Modifications |
|---------|--------------|
| `frontend/lib/types/index.ts` | Aligner tous les types avec le backend |
| `frontend/lib/hooks/useAdmin.ts` | Adapter parsers + payloads |
| `frontend/components/admin/forms/SCIForm.tsx` | Renommer champs + ajouter gérant |
| `frontend/components/admin/forms/BienForm.tsx` | Renommer champs + corriger enums |
| `frontend/components/admin/forms/LocataireForm.tsx` | Vérifier optionnalité + bail |

---

## Ce qui est déjà OK (ne pas toucher)

- `AdminTabs.tsx` — navigation entre onglets ✅
- `BiensTab.tsx`, `LocatairesTab.tsx`, `SCITab.tsx` — structure tableau, modals, actions ✅
- `QuittancesPanel.tsx` — panel quittances ✅
- `DataTable.tsx`, `Modal.tsx`, `Badge.tsx` — composants UI ✅
- `api/client.ts` — configuration Axios + intercepteur auth ✅
- Auth flow (token dans localStorage, redirect 401) ✅
