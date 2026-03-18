# Architecture Frontend - Meziane Monitoring

**Version 3.1 - 17 mars 2026 - Baseline implémentée**

---

## 1. Vision

**Bloomberg Terminal + Perplexity Finance Design**
- Interface **dense** : 12 widgets visibles sans navigation secondaire.
- **Design Perplexity Finance** : fond noir profond, surfaces vitrées, métriques compactes.
- **Dark/Light mode** : toggle global dans le header.
- **Code simple** : composants courts, peu de dépendances, structure lisible.
- **Temps réel** : prévu via WebSocket backend.
- Toutes les infos critiques doivent rester visibles d'un coup d'œil.

---

## 2. Stack Technique

```text
Next.js 16 (App Router)
TypeScript 5
TailwindCSS 4
Recharts
Axios
Zustand
WebSocket
Fontsource local (Inter Variable + JetBrains Mono)
```

**Pas de React Query au début** → Axios direct + `useState` / `useEffect`.

**Pas de shadcn/ui** → composants custom simples.

**Pas de dépendances décoratives** → privilégier la clarté et le temps de livraison.

**Charts en client-only** → import dynamique sans SSR pour éviter les warnings de sizing Recharts en build statique.

---

## 3. Pages de l'Application

### 3.1 Sitemap cible

```text
/ (redirect → /login si non auth, sinon /dashboard)
├── /login
├── /dashboard
├── /agents
│   ├── /agents/new
│   └── /agents/[id]
└── /admin
    ├── /admin/biens
    ├── /admin/sci
    ├── /admin/locataires
    └── /admin/analytics
```

### 3.2 Baseline actuellement livrée

```text
/                         → redirect /dashboard
/login                    → page statique auth
/dashboard                → dashboard Bloomberg mocké
/agents                   → placeholder phase 3
/admin                    → placeholder phase 3
```

### 3.3 Routing Next.js

```text
frontend/src/app/
├── page.tsx
├── (auth)/
│   └── login/page.tsx
└── (dashboard)/
    ├── layout.tsx
    ├── dashboard/page.tsx
    ├── agents/page.tsx
    └── admin/page.tsx
```

---

## 4. Dashboard Bloomberg

### Layout Grid (12 widgets)

```text
┌────────────────┬────────────────┬────────────────┬────────────────┐
│ Patrimoine Net │ Cashflow Today │ Alertes IA     │ Performance YTD│
├────────────────┴────────────────┼────────────────┴────────────────┤
│ Graphique Cashflow 30j          │ Évolution Patrimoine 12m        │
├─────────────────────────────────┼─────────────────────────────────┤
│ Transactions Récentes           │ Top 5 Biens                     │
├─────────────────────────────────┼─────────────────────────────────┤
│ SCI Overview                    │ Locataires                      │
├─────────────────────────────────┼─────────────────────────────────┤
│ Simulation Acquisition          │ Opportunités IA                 │
└─────────────────────────────────┴─────────────────────────────────┘
```

### Widgets

1. `KpiCard` x4
2. `CashflowChart`
3. `PatrimoineChart`
4. `TransactionsTable`
5. `TopBiensList`
6. `SCIOverviewGrid`
7. `LocatairesList`
8. `SimulationPanel`
9. `OpportunitesList`

Le total affiché est bien de **12 widgets** en comptant les 4 KPI séparés.

---

## 5. Structure Dossiers

```text
frontend/src/
├── app/
│   ├── page.tsx
│   ├── globals.css
│   ├── layout.tsx
│   ├── (auth)/login/page.tsx
│   └── (dashboard)/
│       ├── layout.tsx
│       ├── dashboard/page.tsx
│       ├── agents/page.tsx
│       └── admin/page.tsx
├── components/
│   ├── dashboard/
│   │   ├── CashflowChart.tsx
│   │   ├── ChartPanels.tsx
│   │   ├── KpiCard.tsx
│   │   ├── LocatairesList.tsx
│   │   ├── OpportunitesList.tsx
│   │   ├── PatrimoineChart.tsx
│   │   ├── SCIOverviewGrid.tsx
│   │   ├── SimulationPanel.tsx
│   │   ├── TopBiensList.tsx
│   │   └── TransactionsTable.tsx
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── ThemeToggle.tsx
│   ├── providers/
│   │   └── ThemeProvider.tsx
│   └── ui/
│       └── Panel.tsx
└── lib/
    ├── mock/dashboard.ts
    ├── stores/ui-store.ts
    ├── types/dashboard.ts
    └── utils/format.ts
```

### Dossiers prévus pour la phase 2+

```text
frontend/src/lib/
├── api/client.ts
├── hooks/useDashboard.ts
└── hooks/useRealTime.ts
```

---

## 6. Design System

### Principes

- Fond non plat avec gradients diffus et grille discrète.
- Surfaces `glass` avec blur léger.
- Chiffres en `font-mono` tabulaire.
- Panels arrondis et compacts.
- Priorité au contraste et à la lisibilité des métriques.

### Couleurs

```css
Dark :
- background   : #0A0A0A
- foreground   : #F5F7FA
- accent       : #38BDF8
- positive     : #34D399
- negative     : #F87171
- warning      : #FBBF24

Light :
- background   : #F3F5F7
- foreground   : #101828
- accent       : #0EA5E9
- positive     : #059669
- negative     : #DC2626
- warning      : #D97706
```

### Typographie

```text
Texte : Inter Variable
Chiffres : JetBrains Mono Variable
```

### Spacing

```text
Panels : p-5 / p-6
KPI : p-4
Gap principal : gap-4
Charts : h-72
```

---

## 7. Intégration Backend

### API client prévu

```typescript
// lib/api/client.ts
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("jwt_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Stratégie de chargement dashboard

Le point d'entrée cible pour la phase 2 est :

```text
GET /api/dashboard/full
```

Schéma recommandé :

```typescript
const [data, setData] = useState<FullDashboardResponse | null>(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
  api.get("/api/dashboard/full").then((response) => {
    setData(response.data);
    setLoading(false);
  });
}, []);
```

### Real-time prévu

```typescript
useEffect(() => {
  const ws = new WebSocket("ws://localhost:8000/ws");

  ws.onmessage = (event) => {
    const payload = JSON.parse(event.data);
    if (payload.event === "TRANSACTION_CREATED") {
      reloadDashboard();
    }
  };

  return () => ws.close();
}, []);
```

---

## 8. Roadmap Frontend

### Phase 1 : Setup + Dashboard Statique
- Initialisation Next.js + TypeScript
- Setup TailwindCSS + design tokens dark/light
- Layout `Sidebar + Header + ThemeToggle`
- Dashboard 12 widgets en mock
- Login, Admin, Agents en placeholders

### Phase 2 : Intégration API
- `lib/api/client.ts`
- Hook `useDashboard`
- Connexion `/api/dashboard/full`
- Login JWT fonctionnel
- Auth guard et redirections

### Phase 3 : Pages Admin + Agents
- CRUD Biens / SCI / Locataires
- Liste agents
- Configuration agent
- Formulaires métier

### Phase 4 : Real-Time
- Hook `useRealTime`
- Refresh dashboard à réception des événements
- Notifications toast

### Phase 5 : Optimisations
- Virtualisation table transactions
- Lazy loading des zones lourdes
- Responsive mobile finalisé
- Tests E2E

---

## 9. Décisions de mise en œuvre

- Le dashboard est statique au départ pour verrouiller le langage visuel avant le branchement API.
- Le backend expose déjà `/api/dashboard/full`, ce qui réduit le coût de la phase 2.
- Le build local fiable passe aujourd'hui par `next build --webpack`.
- Le build Turbopack sandboxé peut échouer sur des contraintes d'environnement et ne doit pas être utilisé comme signal produit.

---

**Rappel : Concis, clair, net. YAGNI. KISS.**
