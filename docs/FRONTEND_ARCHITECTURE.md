# Architecture Frontend - Meziane Monitoring

**Version 2.0 - 16 mars 2026**

---

## 1. Vision

**Bloomberg Terminal pour patrimoine immobilier**
- Interface **dense** : 12+ widgets simultanés
- **Dark/Light mode** au choix (toggle dans header)
- Mise à jour **temps réel** (WebSocket)
- Toutes infos critiques visibles d'un coup d'œil

---

## 2. Stack Technique

```
Next.js 14 (App Router)
TypeScript 5.3
TailwindCSS 3.4 + shadcn/ui
Recharts (charts)
React Query v5 (state + real-time)
Zustand (UI state)
WebSocket (real-time data)
```

---

## 3. Pages de l'Application

### 3.1 Sitemap

```
/ (redirect → /login si non auth, sinon /dashboard)
├── /login                    # Auth JWT
├── /dashboard                # Bloomberg dashboard (12+ widgets)
├── /agents                   # Liste + config agents IA
│   ├── /agents/new           # Créer nouvel agent
│   └── /agents/[id]          # Config agent existant
└── /admin                    # CRUD biens, SCI, analytics
    ├── /admin/biens
    ├── /admin/sci
    ├── /admin/locataires
    └── /admin/analytics      # Stats clics si partage dashboard
```

### 3.2 Routing Next.js

```
frontend/src/app/
├── (auth)/
│   └── login/page.tsx
├── (dashboard)/
│   ├── layout.tsx            # Sidebar + Header
│   ├── dashboard/page.tsx    # Bloomberg dashboard
│   ├── agents/
│   │   ├── page.tsx
│   │   ├── new/page.tsx
│   │   └── [id]/page.tsx
│   └── admin/
│       ├── page.tsx
│       ├── biens/page.tsx
│       ├── sci/page.tsx
│       ├── locataires/page.tsx
│       └── analytics/page.tsx
```

---

## 4. Dashboard Bloomberg (Page Principale)

### Layout Grid (12 widgets)

```
┌────────────────┬────────────────┬────────────────┬────────────────┐
│ Patrimoine Net │ Cashflow Today │ Alertes IA     │ Performance YTD│
│ 2.4M€ (+3.2%)  │ +12K€          │ 3 nouvelles    │ +18.5%         │
├────────────────┴────────────────┼────────────────┴────────────────┤
│ Graphique Cashflow 30j          │ Évolution Patrimoine 12m        │
│ [Area Chart]                    │ [Line Chart]                    │
├─────────────────────────────────┼─────────────────────────────────┤
│ Transactions Récentes (Table)   │ Top 5 Biens (Cards)             │
│ 10 dernières transactions       │ Tri par TRI décroissant         │
├─────────────────────────────────┼─────────────────────────────────┤
│ SCI Overview (6 mini-cards)     │ Locataires (5 cards)            │
│ Revenus/Biens par SCI           │ Statut paiement                 │
├─────────────────────────────────┼─────────────────────────────────┤
│ Simulation Acquisition          │ Opportunités IA (Agent)         │
│ Formulaire rapide               │ 2 biens trouvés                 │
└─────────────────────────────────┴─────────────────────────────────┘
```

### Widgets Principaux

1. **KPICard** : Patrimoine, Cashflow, Alertes, Performance
2. **CashflowChart** : Area chart 30 jours
3. **PatrimoineChart** : Line chart 12 mois
4. **TransactionsTable** : 10 dernières transactions (tri, filtres)
5. **Top5Biens** : Cards avec TRI + rendement
6. **SCIOverview** : 6 mini-cards (revenus, nb biens, cashflow)
7. **LocatairesCards** : Statut paiement (OK, retard, impayé)
8. **SimulationForm** : Prix, apport, taux → TRI
9. **OpportunitesWidget** : Biens trouvés par agent IA

---

## 5. Page Login

```tsx
// app/(auth)/login/page.tsx
Formulaire email/password
→ POST /api/auth/login
→ Store JWT token (localStorage)
→ Redirect /dashboard
```

Design : Centré, minimal, dark theme

---

## 6. Page Agents IA

### Liste agents (`/agents`)

```
┌─────────────────────────────────────────────────────────┐
│ Agent                  │ Statut  │ Dernière exec │ Actions│
├────────────────────────┼─────────┼───────────────┼────────┤
│ Prospection SeLoger    │ ✅ Actif│ Il y a 2h     │ ⚙️ 🗑️  │
│ Analyse Bien           │ ✅ Actif│ Il y a 30min  │ ⚙️ 🗑️  │
│ Veille Réglementaire   │ ⏸️ Pause│ -             │ ▶️ ⚙️  │
└────────────────────────┴─────────┴───────────────┴────────┘

[+ Créer Nouvel Agent]
```

### Config agent (`/agents/[id]`)

```
Formulaire :
- Nom agent
- Type (Prospection / Analyse / Veille)
- Fréquence exécution (quotidien, hebdo)
- Critères (prix min/max, ville, rendement cible)
- Actif/Pause

[Logs Historique]
Table : Date | Action | Résultat
```

### Créer agent (`/agents/new`)

Même formulaire que config, sans logs.

---

## 7. Page Admin

### Structure

```
/admin
├── Biens       → DataTable + Modal create/edit
├── SCI         → DataTable + Modal create/edit
├── Locataires  → DataTable + Modal create/edit
└── Analytics   → Stats clics si dashboard partagé (Google Analytics style)
```

### Admin Biens (`/admin/biens`)

```
DataTable :
Colonnes : Adresse | SCI | Prix | Loyer | TRI | Actions (✏️ 🗑️)

Modal Create/Edit :
- Adresse complète
- SCI (select)
- Prix acquisition
- Loyer mensuel
- Upload photo (optionnel)
```

### Admin Analytics (`/admin/analytics`)

Si dashboard partagé (future feature) :
- Nb vues dashboard
- Clics par widget
- Temps moyen session

---

## 8. Structure Dossiers

```
frontend/src/
├── app/
│   ├── (auth)/login/page.tsx
│   └── (dashboard)/
│       ├── layout.tsx                 # Sidebar + auth check
│       ├── dashboard/page.tsx         # Bloomberg dashboard
│       ├── agents/...
│       └── admin/...
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   └── Header.tsx
│   ├── widgets/                       # 9 widgets Bloomberg
│   │   ├── KPICard.tsx
│   │   ├── CashflowChart.tsx
│   │   ├── TransactionsTable.tsx
│   │   └── ...
│   ├── forms/
│   │   ├── BienForm.tsx
│   │   ├── AgentForm.tsx
│   │   └── SimulationForm.tsx
│   └── ui/                            # shadcn/ui
├── lib/
│   ├── api/
│   │   ├── client.ts                  # axios + JWT interceptor
│   │   ├── cashflow.ts
│   │   ├── patrimoine.ts
│   │   └── agents.ts
│   ├── hooks/
│   │   ├── useRealTime.ts             # WebSocket hook
│   │   ├── useCashflow.ts             # React Query
│   │   └── usePatrimoine.ts
│   ├── stores/
│   │   └── ui-store.ts                # Zustand (sidebar collapse, etc.)
│   ├── types/
│   │   └── index.ts                   # Types backend
│   └── utils/
│       ├── format.ts                  # Format €, %, dates
│       └── calc.ts                    # Calculs TRI, cashflow
└── styles/
    └── globals.css
```

---

## 9. Design System

### Couleurs (Dark/Light Mode)

```css
DARK MODE (par défaut) :
Background : bg-slate-950
Text       : text-slate-200
Border     : border-slate-800

LIGHT MODE :
Background : bg-white
Text       : text-slate-900
Border     : border-slate-200

Accents (identiques dark/light) :
- Revenus/Positif : text-emerald-500 (dark) / text-emerald-600 (light)
- Dépenses/Négatif : text-red-500 (dark) / text-red-600 (light)
- Neutre/Info     : text-cyan-500 (dark) / text-cyan-600 (light)
- Warning         : text-amber-500 (dark) / text-amber-600 (light)
```

### Toggle Dark/Light Mode

```typescript
// Composant ThemeToggle dans Header
// Zustand store pour persister choix (localStorage)
// Classes Tailwind : dark:bg-slate-950 bg-white
```

### Typographie

```
Font : Inter Variable
Chiffres : JetBrains Mono (font-mono, tabular-nums)
```

### Spacing (Dense)

```
Widgets : p-4, gap-2
KPI Cards : p-3
Charts : h-64
```

---

## 10. Intégration Backend

### API Client

```typescript
// lib/api/client.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
```

### React Query Hook Exemple

```typescript
// lib/hooks/useCashflow.ts
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api/client';

export function useCashflow() {
  return useQuery({
    queryKey: ['cashflow'],
    queryFn: async () => {
      const { data } = await api.get('/api/cashflow');
      return data;
    },
    refetchInterval: 30000, // 30s
  });
}
```

### WebSocket Real-Time

```typescript
// lib/hooks/useRealTime.ts
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws');

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.event === 'TRANSACTION_CREATED') {
      queryClient.invalidateQueries(['cashflow']);
    }
  };

  return () => ws.close();
}, []);
```

---

## 11. Roadmap Frontend

### Phase 1 : Setup + Dashboard Statique (3 jours)
- Init Next.js 14 + TypeScript
- Setup TailwindCSS + shadcn/ui
- Layout sidebar + header
- 12 widgets avec mock data
- Design system complet

### Phase 2 : Intégration API (3 jours)
- API client + JWT
- React Query hooks
- Connexion backend réel
- Page Login fonctionnelle

### Phase 3 : Pages Admin + Agents (3 jours)
- CRUD Biens, SCI, Locataires
- Page Agents (liste + config)
- Formulaires + validation

### Phase 4 : Real-Time (2 jours)
- WebSocket connection
- Auto-invalidation cache React Query
- Toast notifications

### Phase 5 : Optimisations (2 jours)
- Virtualisation tables
- Lazy loading
- Mobile responsive
- Tests E2E

---

**FIN - 300 lignes**

**Rappel : Concis, clair, net. YAGNI. KISS.**
