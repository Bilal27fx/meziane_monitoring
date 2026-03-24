# RFC-002 — Routes backend quittances

| Champ | Valeur |
|-------|--------|
| **ID** | RFC-002 |
| **Type** | feature |
| **Priorité** | HAUTE |
| **Statut** | En attente |
| **Ouvert le** | 2026-03-24 |
| **Clôturé le** | — |

---

## Problème

Le frontend appelle `GET /api/locataires/{id}/quittances` mais aucune route n'existe en backend.
Le modèle `Quittance` existe (`backend/app/models/quittance.py`) mais n'est pas exposé via API.

---

## Routes à créer

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/locataires/{locataire_id}/quittances` | Liste des quittances d'un locataire |
| `GET` | `/api/quittances/{id}/pdf` | Téléchargement PDF quittance |
| `POST` | `/api/locataires/{locataire_id}/quittances/generer` | Génère quittance du mois courant |

---

## Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/api/quittance_routes.py` | Créer |
| `backend/app/schemas/quittance_schema.py` | Créer |
| `backend/app/main.py` | Ajouter import + `app.include_router` |

---

## Structure du modèle Quittance (existant)

```python
# backend/app/models/quittance.py
class Quittance(Base):
    id: int
    bail_id: int          # FK → baux.id
    mois: int             # 1-12
    annee: int
    montant_loyer: float
    montant_charges: float
    montant_total: float
    date_paiement: date | None
    montant_paye: float | None
    statut: StatutQuittance  # en_attente | paye | impaye | partiel
    fichier_url: str | None
```

---

## Schema de réponse attendu par le frontend

```typescript
// frontend/lib/types/index.ts
interface Quittance {
  id: number
  locataire_id: number
  mois: string          // "janvier 2026" (formaté)
  montant: number
  statut: 'payee' | 'en_attente' | 'impayee'
  date_paiement?: string
  created_at: string
}
```

**Note :** le frontend attend `statut: 'payee'` mais le modèle stocke `StatutQuittance.PAYE = 'paye'`.
Mapper dans le schema Pydantic ou adapter le frontend.

---

## Dépendances

- RFC-004 dépend de cette RFC (boutons QuittancesPanel)

---

## Tests à effectuer après correction

- [ ] `GET /api/locataires/1/quittances` retourne la liste
- [ ] Le `QuittancesPanel` affiche les vraies quittances (plus de mock data)
- [ ] `POST /api/locataires/1/quittances/generer` crée une quittance en BDD
