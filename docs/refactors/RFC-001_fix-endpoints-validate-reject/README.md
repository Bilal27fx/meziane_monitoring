# RFC-001 — Fix endpoints validate/reject

| Champ | Valeur |
|-------|--------|
| **ID** | RFC-001 |
| **Type** | bugfix |
| **Priorité** | CRITIQUE |
| **Statut** | En attente |
| **Ouvert le** | 2026-03-24 |
| **Clôturé le** | — |

---

## Problème

Le frontend appelle des endpoints en anglais, le backend les expose en français.

| Frontend (actuel) | Backend (attendu) |
|-------------------|-------------------|
| `POST /api/transactions/{id}/validate` | `POST /api/transactions/{id}/valider` |
| `POST /api/transactions/{id}/reject` | `POST /api/transactions/{id}/rejeter` |

**Impact :** toute validation ou rejet de transaction retourne `404 Not Found`.

---

## Fichiers à modifier

### `frontend/lib/hooks/useAdmin.ts`

```diff
// ligne 185
- mutationFn: (id: number) => api.post(`/api/transactions/${id}/validate`),
+ mutationFn: (id: number) => api.post(`/api/transactions/${id}/valider`),

// ligne 193
- mutationFn: (id: number) => api.post(`/api/transactions/${id}/reject`),
+ mutationFn: (id: number) => api.post(`/api/transactions/${id}/rejeter`),
```

---

## Tests à effectuer après correction

- [ ] Cliquer "Valider" sur une transaction en attente → statut passe à `valide`
- [ ] Cliquer "Rejeter" sur une transaction en attente → statut passe à `rejete`
- [ ] Vérifier aucun 404 dans la console navigateur

---

## Risques

Aucun — correction de 2 lignes, zéro impact sur d'autres fonctionnalités.
