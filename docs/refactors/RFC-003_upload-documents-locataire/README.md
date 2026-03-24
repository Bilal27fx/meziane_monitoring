# RFC-003 — Upload documents locataire

| Champ | Valeur |
|-------|--------|
| **ID** | RFC-003 |
| **Type** | feature |
| **Priorité** | MOYENNE |
| **Statut** | En attente |
| **Ouvert le** | 2026-03-24 |
| **Clôturé le** | — |

---

## Problème

Dans `LocataireForm.tsx`, la zone "Glisser-déposer les documents" est purement décorative.
Aucun `<input type="file">`, aucun handler, aucun appel API.

Le backend a pourtant un endpoint complet :
```
POST /api/documents/upload-locataire
  Body (multipart/form-data):
    - locataire_id: int
    - type_document: TypeDocument (enum)
    - file: UploadFile
    - sci_id?: int (optionnel, déduit automatiquement)
    - date_document?: date
```

---

## Fichiers à modifier

| Fichier | Action |
|---------|--------|
| `frontend/components/admin/forms/LocataireForm.tsx` | Modifier — section Documents (lignes 249-255) |

---

## Implémentation attendue

```tsx
// État à ajouter
const [pendingFiles, setPendingFiles] = useState<
  Array<{ file: File; type: TypeDocument }>
>([])

// Input caché cliqué par la div
<input
  type="file"
  ref={fileInputRef}
  multiple
  accept=".pdf,.jpg,.jpeg,.png"
  className="hidden"
  onChange={handleFileSelect}
/>

// Zone cliquable
<div onClick={() => fileInputRef.current?.click()} ...>
  ...
</div>

// Upload dans handleSubmit (après création/mise à jour locataire)
for (const { file, type } of pendingFiles) {
  const fd = new FormData()
  fd.append('locataire_id', String(locataireId))
  fd.append('type_document', type)
  fd.append('file', file)
  await api.post('/api/documents/upload-locataire', fd)
}
```

---

## TypeDocument enum (backend)

```
PIECE_IDENTITE | JUSTIFICATIF_DOMICILE | CONTRAT_TRAVAIL
FICHE_PAIE | AVIS_IMPOSITION | RIB | ASSURANCE_HABITATION
ACTE_CAUTION_SOLIDAIRE | QUITTANCE_LOYER_PRECEDENTE | BAIL | AUTRE
```

---

## Tests à effectuer après correction

- [ ] Cliquer la zone → ouvre le sélecteur de fichier
- [ ] Sélectionner un PDF → apparaît dans la liste
- [ ] Sauvegarder le locataire → document uploadé en BDD + MinIO
- [ ] `GET /api/documents/locataire/{id}` retourne le document
