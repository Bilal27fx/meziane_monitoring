# RFC-004 — Boutons QuittancesPanel connectés API

| Champ | Valeur |
|-------|--------|
| **ID** | RFC-004 |
| **Type** | bugfix |
| **Priorité** | MOYENNE |
| **Statut** | En attente |
| **Ouvert le** | 2026-03-24 |
| **Clôturé le** | — |
| **Bloqué par** | RFC-002 (routes quittances backend) |

---

## Problème

Dans `QuittancesPanel.tsx`, deux boutons affichent un toast sans faire d'appel API.

```typescript
// ligne 34 — toast only, pas d'appel API
const handleDownload = (mois: string) => {
  toast.success(`Quittance ${mois} téléchargée`)
}

// ligne 38 — toast only, pas d'appel API
const handleGenerate = () => {
  toast.success('Quittance générée et envoyée par email')
}
```

---

## Fichiers à modifier

| Fichier | Action |
|---------|--------|
| `frontend/components/admin/panels/QuittancesPanel.tsx` | Modifier lignes 34-40 |
| `frontend/lib/hooks/useAdmin.ts` | Ajouter hooks `useDownloadQuittance` + `useGenerateQuittance` |

---

## Correction attendue

### handleDownload
```typescript
const handleDownload = async (quittanceId: number, mois: string) => {
  try {
    const response = await api.get(`/api/quittances/${quittanceId}/pdf`, {
      responseType: 'blob'
    })
    const url = URL.createObjectURL(response.data)
    window.open(url, '_blank')
    toast.success(`Quittance ${mois} téléchargée`)
  } catch {
    toast.error('Erreur lors du téléchargement')
  }
}
```

### handleGenerate
```typescript
const generateQuittance = useGenerateQuittance()

const handleGenerate = async () => {
  try {
    await generateQuittance.mutateAsync(locataireId)
    toast.success('Quittance générée et envoyée par email')
  } catch {
    toast.error('Erreur lors de la génération')
  }
}
```

---

## Dépendances

- **Bloqué par RFC-002** — les routes `GET /api/quittances/{id}/pdf` et `POST /api/locataires/{id}/quittances/generer` doivent exister.

---

## Tests à effectuer après correction

- [ ] Cliquer PDF → ouvre le PDF dans un onglet
- [ ] Cliquer "Générer quittance" → quittance créée + email envoyé
- [ ] Erreur API → toast d'erreur visible (pas de toast success faux)
