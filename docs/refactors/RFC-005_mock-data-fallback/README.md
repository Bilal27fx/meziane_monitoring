# RFC-005 — Suppression mock data fallback silencieux

| Champ | Valeur |
|-------|--------|
| **ID** | RFC-005 |
| **Type** | refactor |
| **Priorité** | BASSE |
| **Statut** | En attente |
| **Ouvert le** | 2026-03-24 |
| **Clôturé le** | — |

---

## Problème

Dans `useAdmin.ts`, tous les hooks de lecture ont un catch qui retourne silencieusement des données mock si l'API est down. L'utilisateur ne voit aucune erreur.

```typescript
// Exemple actuel — tous les hooks ont ce pattern
queryFn: async () => {
  try {
    const response = await api.get('/api/sci', { params })
    return response.data
  } catch {
    // SILENCIEUX — l'user voit des données fictives sans savoir que l'API est down
    return { items: MOCK_SCIS, total: MOCK_SCIS.length, page: 1, per_page: 20, pages: 1 }
  }
}
```

**Hooks impactés :** `useSCIs`, `useBiens`, `useLocataires`, `useTransactions`, `useQuittances`

---

## Fichiers à modifier

| Fichier | Action |
|---------|--------|
| `frontend/lib/hooks/useAdmin.ts` | Supprimer blocs catch + constantes MOCK_* |

---

## Correction attendue

```typescript
// Après correction — React Query gère isError nativement
export function useSCIs(params?: SCIParams) {
  return useQuery({
    queryKey: ['scis', params],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<SCI>>('/api/sci', { params })
      return response.data
    },
  })
}
```

Les composants utilisent déjà `isLoading` et `data` depuis les hooks — ajouter `isError` là où c'est pertinent pour afficher un `EmptyState` d'erreur.

---

## Impact UI

Dans les onglets (BiensTab, LocatairesTab, etc.), ajouter la gestion de `isError` :
```tsx
if (isError) return <EmptyState message="Impossible de charger les données" />
```

---

## Tests à effectuer après correction

- [ ] Backend éteint → tableau affiche un état d'erreur (pas de données fictives)
- [ ] Backend rallumé → tableau se recharge automatiquement (React Query retry)
- [ ] Aucune constante MOCK_* restante dans `useAdmin.ts`

---

## Note

Les mocks peuvent être conservés dans un fichier séparé `lib/mocks/` si besoin de storybook ou de tests unitaires frontend.
