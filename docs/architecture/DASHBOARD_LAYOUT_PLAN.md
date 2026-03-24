# Dashboard Layout Plan — Meziane Monitoring
**Version 3.0 — 23 mars 2026**
**Cible : 1920×1080px · Sans scroll · Style Perplexity Finance**

---

## Vue d'ensemble (1920×1080)

```
┌── SIDEBAR 48px ──┬────────────────────── MAIN CONTENT 1872px ────────────────────────┐
│                  │ HEADER h-14 (56px)                                                  │
│  M               ├─────────────────────────────────────────────────────────────────────┤
│                  │ DASHBOARD GRID — p-3 gap-2                                          │
│  ▤ Dashboard     │                                                                      │
│                  │  ┌──────────────┬──────────────┬──────────────┬──────────────────┐  │
│  ⚡ Agent         │  │ PATRIMOINE   │ CASHFLOW     │ ALERTES      │ PERFORMANCE      │  │
│                  │  │ NET          │ DU MOIS      │ IA           │ YTD              │  │
│  ⚙ Admin         │  │ 2.4M€ ▲3.2% │ +12 300€     │ 3 actives    │ +18.5%          │  │
│                  │  │ h-14         │ h-14         │ h-14         │ h-14             │  │
│                  │  ├──────────────┴──────────────┴──────────────┤                  │  │
│                  │  │ CASHFLOW 30J │ PATRIMOINE   │ SCI OVERVIEW │ TOP 5 BIENS      │  │
│                  │  │ [Area Chart] │ 12M          │ 3 mini-cards │ (row-span-3)     │  │
│  ·               │  │             │ [Line Chart] │ par SCI      │ #1 42 av...  9.2%│  │
│  B               │  │             │             │ Facha: +4750 │ #2 Studio... 7.8%│  │
│                  │  │ h-48        │ h-48        │ h-48         │ #3 Local...  6.1%│  │
└──────────────────┘  ├─────────────────────────────────────────────┤ #4 Hôtel... 5.4%│  │
                      │ TRANSACTIONS RÉCENTES (col-span-9)          │                  │  │
                      │ Date │ SCI │ Libellé │ Catégorie │ Montant  │ #5 ...      4.8%│  │
                      │ 7 lignes max · h-48                         │                  │  │
                      ├──────────────┬──────────────┬───────────────┤ h-full (3×h-48) │  │
                      │ SIMULATION   │ OPPORTUNITÉS │ LOCATAIRES    │                  │  │
                      │ ACQUISITION  │ IA (top 2)   │ (top 4)       │                  │  │
                      │ h-48         │ h-48         │ h-48          │                  │  │
                      └──────────────┴──────────────┴───────────────┴──────────────────┘  │
                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Grid CSS — Implémentation

```tsx
// app/(app)/dashboard/page.tsx

export default function DashboardPage() {
  return (
    <div className="h-[calc(100vh-56px)] p-3 overflow-hidden">
      <div className="grid grid-cols-12 grid-rows-[56px_192px_192px_192px] gap-2 h-full">

        {/* ═══════════════════════════════════════════
            ROW 1 — 4 KPI Cards (h=56px)
        ═══════════════════════════════════════════ */}
        <div className="col-span-3 row-span-1">
          <KPICard
            title="Patrimoine Net"
            value={formatCurrency(data.kpi.patrimoine_net)}
            change={data.kpi.performance_ytd}
            trend="up"
            icon={TrendingUp}
          />
        </div>
        <div className="col-span-3 row-span-1">
          <KPICard
            title="Cashflow du Mois"
            value={formatCurrency(data.kpi.cashflow_today)}
            trend={data.kpi.cashflow_today > 0 ? "up" : "down"}
            icon={Wallet}
          />
        </div>
        <div className="col-span-3 row-span-1">
          <KPICard
            title="Alertes Actives"
            value={String(data.kpi.nb_alertes)}
            trend={data.kpi.nb_alertes > 0 ? "down" : "up"}
            icon={Bell}
          />
        </div>
        <div className="col-span-3 row-span-1">
          <KPICard
            title="Performance YTD"
            value={`${data.kpi.performance_ytd > 0 ? '+' : ''}${data.kpi.performance_ytd.toFixed(1)}%`}
            change={data.kpi.performance_ytd}
            trend={data.kpi.performance_ytd > 0 ? "up" : "down"}
            icon={BarChart2}
          />
        </div>

        {/* ═══════════════════════════════════════════
            ROW 2 — Charts + SCI Overview + Top5 (début)
        ═══════════════════════════════════════════ */}
        <div className="col-span-3 row-span-1">
          <CashflowChart data={data.cashflow_30days} />
        </div>
        <div className="col-span-3 row-span-1">
          <PatrimoineChart data={data.patrimoine_12months} />
        </div>
        <div className="col-span-3 row-span-1">
          <SCIOverview scis={data.sci_overview} />
        </div>
        <div className="col-span-3 row-span-3">  {/* ← S'étend sur 3 lignes */}
          <Top5Biens biens={data.top_biens} />
        </div>

        {/* ═══════════════════════════════════════════
            ROW 3 — Transactions Table (large)
        ═══════════════════════════════════════════ */}
        <div className="col-span-9 row-span-1">
          <TransactionsTable transactions={data.recent_transactions} />
        </div>
        {/* Top5Biens continue (row-span-3) */}

        {/* ═══════════════════════════════════════════
            ROW 4 — Simulation + Opportunités + Locataires
        ═══════════════════════════════════════════ */}
        <div className="col-span-3 row-span-1">
          <SimulationForm />
        </div>
        <div className="col-span-3 row-span-1">
          <OpportunitesWidget opportunites={data.opportunites} />
        </div>
        <div className="col-span-3 row-span-1">
          <LocatairesCards locataires={data.locataires} />
        </div>
        {/* Top5Biens se termine ici */}

      </div>
    </div>
  )
}
```

---

## Calcul Hauteur Totale

```
Zone utile = 1080px
├── Header : 56px
└── Dashboard : 1080 - 56 = 1024px

Grid rows :
├── p-3 top          : 12px
├── Row 1 (KPI)      : 56px
├── gap-2            :  8px
├── Row 2 (Charts)   : 192px
├── gap-2            :  8px
├── Row 3 (Transac.) : 192px
├── gap-2            :  8px
├── Row 4 (Sim/Opp)  : 192px
└── p-3 bottom       : 12px
                     ─────────
TOTAL               : 680px ✅

Espace libre sur 1024px : 344px
→ Possibilité d'augmenter les charts à h-56 (224px) si souhaité
```

---

## Spécifications Pixel par Pixel

### KPICard (h=56px)

```
┌────────────────────────────────────────────────────┐  56px
│ [Icon 14px]  PATRIMOINE NET           ▲ +3.2%      │  ← ligne 1 (h=18px)
│              2 400 000 €                           │  ← ligne 2 (h=24px)
│              Valeur totale biens                   │  ← ligne 3 (h=14px) optionnel
└────────────────────────────────────────────────────┘
padding: p-2 (8px)
```

```tsx
<div className="h-14 p-2 bg-[#111111] border border-neutral-800 rounded-md flex items-center gap-3">
  <div className="text-neutral-600">
    <Icon className="h-3.5 w-3.5" />
  </div>
  <div className="flex-1 min-w-0">
    <p className="text-[10px] text-neutral-500 uppercase tracking-wide truncate">{title}</p>
    <p className="text-base font-semibold font-mono text-white tabular-nums leading-tight">{value}</p>
  </div>
  {change !== undefined && (
    <div className={cn("text-[10px] font-mono font-medium shrink-0", trend === "up" ? "text-green-500" : "text-red-500")}>
      {trend === "up" ? "▲" : "▼"} {Math.abs(change).toFixed(1)}%
    </div>
  )}
</div>
```

---

### CashflowChart (h=192px)

```
┌────────────────────────────────────────────────────┐  192px
│ Cashflow 30j          +12 300€ ce mois             │  ← 24px
│ ───────────────────────────────────────────────── │   ← 1px
│                                                    │
│  ████                                              │
│ ██████ █  █    █       ████                        │  ← 144px (chart)
│ ██████████ █████████████████                       │
│ ──────────────────────────── (axes)               │
└────────────────────────────────────────────────────┘
padding: p-2
```

```tsx
<div className="h-48 p-2 bg-[#111111] border border-neutral-800 rounded-md flex flex-col">
  <div className="flex items-baseline justify-between mb-1">
    <span className="text-[10px] text-neutral-500 uppercase tracking-wide">Cashflow 30j</span>
    <span className="text-xs font-mono font-semibold text-green-500 tabular-nums">
      +{formatCurrency(totalMonth)}
    </span>
  </div>
  <div className="flex-1">
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 2, right: 2, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="cashflowGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis
          dataKey="date" tick={{ fontSize: 8, fill: '#525252' }}
          tickLine={false} axisLine={false}
          tickFormatter={(d) => format(new Date(d), 'dd/MM')}
        />
        <YAxis hide />
        <CartesianGrid strokeDasharray="2 2" stroke="#1a1a1a" vertical={false} />
        <Tooltip
          contentStyle={{ background: '#1a1a1a', border: '1px solid #404040', borderRadius: 4, fontSize: 10 }}
          labelFormatter={(d) => format(new Date(d), 'dd MMM')}
          formatter={(v: number) => [formatCurrency(v), '']}
        />
        <Area type="monotone" dataKey="net" stroke="#22c55e" strokeWidth={1.5}
          fill="url(#cashflowGrad)" dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  </div>
</div>
```

---

### PatrimoineChart (h=192px)

Identique à CashflowChart mais :
```tsx
stroke="#3b82f6"   // blue
fill="url(#patrimoineGrad)"  // blue gradient
dataKey="valeur"
formatter={(v) => formatCurrency(v)}
```

---

### SCIOverview (h=192px)

```
┌────────────────────────────────────────────────────┐
│ SCI Overview                              3 SCI    │  ← header 20px
│ ┌────────────┬────────────┬────────────┐           │
│ │ SCI Facha  │ La Renas.  │ [SCI 3]   │           │
│ │ 2 biens    │ 1 bien     │ 1 bien    │           │
│ │ +2 300€/m  │ +3 000€/m  │ +3 000€/m │           │  ← 3 cards row 1
│ ├────────────┼────────────┼────────────┤           │
│ │ 680 000€   │ 120 000€   │ N/A       │           │
│ │ patrimoine │ patrimoine │           │           │  ← 3 cards row 2
│ └────────────┴────────────┴────────────┘           │
└────────────────────────────────────────────────────┘
```

```tsx
<div className="h-48 p-2 bg-[#111111] border border-neutral-800 rounded-md flex flex-col">
  <div className="flex items-center justify-between mb-1.5">
    <span className="text-[10px] text-neutral-500 uppercase tracking-wide">SCI Overview</span>
    <span className="text-[9px] text-neutral-600">{scis.length} SCI</span>
  </div>
  <div className="grid grid-cols-3 gap-1.5 flex-1">
    {scis.map((sci) => (
      <div key={sci.id} className="bg-[#0d0d0d] border border-neutral-800 rounded p-1.5 flex flex-col gap-0.5">
        <span className="text-[10px] text-neutral-400 font-medium truncate">{sci.nom}</span>
        <span className="text-xs text-white font-mono font-semibold tabular-nums">
          {sci.cashflow_annuel > 0 ? '+' : ''}{formatCurrency(sci.revenus_annuels / 12)}<span className="text-[9px] text-neutral-600">/m</span>
        </span>
        <span className="text-[9px] text-neutral-600">{sci.nb_biens} bien{sci.nb_biens > 1 ? 's' : ''}</span>
        <span className="text-[9px] font-mono text-neutral-500 tabular-nums">{formatCurrency(sci.valeur_patrimoniale)}</span>
      </div>
    ))}
  </div>
</div>
```

---

### Top5Biens (col-span-3, row-span-3 = h=~608px)

```
┌────────────────────────────────────────────────────┐
│ Top 5 Biens               par TRI net · YTD 2026  │  ← 24px
│ ─────────────────────────────────────────────────  │   ← 1px
│ 1  42 av. Victor Hugo, 75018     ████████  9.2%   │
│    SCI Facha · 350 000€                            │  ← ~100px par item
│                                                    │
│ 2  Studio Paris 18e              ███████   7.8%   │
│    SCI Facha · 280 000€                            │
│                                                    │
│ 3  Local commercial 18e          ██████   28.0%   │
│    SCI La Renaissance · 120K€                     │
│                                                    │
│ 4  Hôtel de Bordeaux             █████    —        │
│    SCI [Nom] · N/A                                │
│                                                    │
│ 5  (prochain bien)               —        —        │
│    —                                               │
└────────────────────────────────────────────────────┘
scrollable si débordement
```

```tsx
<div className="h-full p-2 bg-[#111111] border border-neutral-800 rounded-md flex flex-col">
  <div className="flex items-center justify-between mb-2">
    <span className="text-[10px] text-neutral-500 uppercase tracking-wide">Top 5 Biens</span>
    <span className="text-[9px] text-neutral-600 font-mono">TRI Net · YTD {year}</span>
  </div>
  <div className="flex-1 overflow-y-auto space-y-1.5 scrollbar-none">
    {biens.map((bien, i) => (
      <div key={bien.id} className="group p-2 bg-[#0d0d0d] border border-neutral-800 rounded hover:border-neutral-700 transition-colors cursor-pointer">
        <div className="flex items-start gap-2">
          <span className="text-[10px] text-neutral-600 font-mono w-4 shrink-0 mt-0.5">{i + 1}</span>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-white truncate">{bien.adresse}</p>
            <p className="text-[9px] text-neutral-600 truncate">{bien.sci_nom} · {formatCurrency(bien.valeur_actuelle)}</p>
            <div className="mt-1.5 flex items-center gap-2">
              <div className="flex-1 bg-neutral-800 rounded-full h-1">
                <div
                  className="h-1 rounded-full bg-green-500"
                  style={{ width: `${Math.min((bien.rentabilite_nette / 12) * 100, 100)}%` }}
                />
              </div>
              <span className={cn(
                "text-[10px] font-mono font-semibold tabular-nums shrink-0",
                bien.rentabilite_nette > 7 ? "text-green-500" :
                bien.rentabilite_nette > 4 ? "text-yellow-500" : "text-red-400"
              )}>
                {bien.rentabilite_nette > 0 ? '+' : ''}{bien.rentabilite_nette.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      </div>
    ))}
  </div>
</div>
```

---

### TransactionsTable (col-span-9, h=192px)

```
┌────────────────────────────────────────────────────────────────────────┐  192px
│ Transactions Récentes                        [+ Ajouter] [Voir toutes]│  ← 24px
│ DATE     SCI      LIBELLÉ              CATÉGORIE   MONTANT  STATUT     │  ← header (20px)
│ ──────── ──────── ──────────────────── ──────────  ──────── ────────── │   ← 1px
│ 15/03/26 Facha    Loyer Mars J.Dupont  🏠 Loyer    +1 450€  [Validé]  │
│ 15/03/26 Facha    Loyer Mars M.Martin  🏠 Loyer     +850€  [Validé]   │
│ 14/03/26 Renas.   Loyer Local comm.   🏠 Loyer    +3 000€  [Validé]   │
│ 12/03/26 Facha    Répar. chaudière    🔧 Travaux    -650€  [Validé]   │
│ 10/03/26 Facha    Taxe foncière       📋 Taxe     -1 200€  [Attente]  │
│ 05/03/26 Renas.   Frais compta        💼 Honoraires  -350€ [Validé]   │
│ 01/03/26 Hôtel    Loyer Hôtel Mars    🏠 Loyer    +3 000€  [Validé]   │
└────────────────────────────────────────────────────────────────────────┘
max 7 lignes · hover pour voir boutons action
```

```tsx
<div className="h-48 p-2 bg-[#111111] border border-neutral-800 rounded-md flex flex-col">
  <div className="flex items-center justify-between mb-1.5 shrink-0">
    <span className="text-[10px] text-neutral-500 uppercase tracking-wide">Transactions Récentes</span>
    <Link href="/admin" className="text-[9px] text-neutral-600 hover:text-white transition-colors">
      Voir toutes →
    </Link>
  </div>
  <div className="flex-1 overflow-hidden">
    <table className="w-full">
      <thead>
        <tr className="border-b border-neutral-800">
          {['Date', 'SCI', 'Libellé', 'Catégorie', 'Montant', 'Statut'].map(h => (
            <th key={h} className="text-[9px] text-neutral-600 uppercase tracking-wider font-medium text-left pb-1 px-1">{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {transactions.slice(0, 7).map((tx) => (
          <tr key={tx.id} className="border-b border-neutral-800/30 hover:bg-neutral-900/50 group">
            <td className="text-[10px] font-mono text-neutral-400 py-1 px-1 whitespace-nowrap">
              {formatDate(tx.date)}
            </td>
            <td className="text-[10px] text-neutral-500 py-1 px-1 max-w-[60px] truncate">{tx.sci_nom}</td>
            <td className="text-[10px] text-white py-1 px-1 max-w-[180px] truncate">{tx.libelle}</td>
            <td className="py-1 px-1">
              <span className="text-[9px] bg-neutral-800 text-neutral-400 px-1 rounded">
                {tx.categorie ?? '—'}
              </span>
            </td>
            <td className={cn("text-[10px] font-mono font-semibold py-1 px-1 tabular-nums text-right whitespace-nowrap",
              tx.montant > 0 ? "text-green-500" : "text-red-400")}>
              {tx.montant > 0 ? '+' : ''}{formatCurrency(tx.montant)}
            </td>
            <td className="py-1 px-1">
              <StatutBadge statut={tx.statut_validation} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
</div>
```

---

### SimulationForm (h=192px)

```
┌──────────────────────────────────────────────────┐  192px
│ Simulateur Acquisition                           │  ← 24px
│ ──────────────────────────────────────────────   │
│ Prix      [250 000          €]                   │
│ Apport    [50 000           €]                   │
│ Taux      [3.5              %]                   │
│ ──────────────────────────────────────────────   │
│ TRI Brut    9.2%   Mensualité  1 127€/mois       │
│ TRI Net     6.8%   CF Net       +232€/mois       │
│ ──────────────────────────────────────────────   │
│              [Recalculer]                        │
└──────────────────────────────────────────────────┘
calcul côté client en temps réel (pas d'API)
```

```tsx
// Calcul côté client (lib/utils/calc.ts)
// Entrées : prix, apport, taux, durée=20ans
// Sorties calculées en live avec useMemo :
//   mensualite = PMT(taux/12, durée*12, -(prix-apport))
//   loyer_estime = prix * 0.006  // hypothèse 0.6% mensuel
//   cashflow_net = loyer_estime - mensualite - charges
//   tri_brut = (loyer_estime * 12) / prix * 100
//   tri_net = (cashflow_net * 12) / prix * 100
```

---

### OpportunitesWidget (h=192px)

```
┌────────────────────────────────────────────────────┐  192px
│ Opportunités IA              [3 nouvelles]          │  ← 24px
│ ────────────────────────────────────────────────── │
│ ● 92  Paris 18e · 2P · 52m²                        │
│       485 000€ · TRI estimé: 7.8% · DPE: C         │
│       [VU] [→ Analyser]                             │
│ ────────────────────────────────────────────────── │
│ ● 87  Lyon 3e · 3P · 68m²                          │
│       320 000€ · TRI estimé: 8.2% · DPE: B         │
│       [VU] [→ Analyser]                             │
│ ────────────────────────────────────────────────── │
│                    [Voir toutes →IA]                │
└────────────────────────────────────────────────────┘
```

---

### LocatairesCards (h=192px)

```
┌────────────────────────────────────────────────────┐  192px
│ Locataires                   2 actifs              │  ← 24px
│ ─────────────────────────────────────────────────  │
│ ● Jean Dupont                        À jour ✓      │
│   42 av. Victor Hugo · 1 450€/mois                 │
│ ─────────────────────────────────────────────────  │
│ ⚠ Marie Martin                       J+8 ↑         │
│   Studio Paris 18e · 850€/mois                     │
│ ─────────────────────────────────────────────────  │
│ (locataire 3 si applicable)                        │
│ ─────────────────────────────────────────────────  │
│ (locataire 4 si applicable)                        │
└────────────────────────────────────────────────────┘
```

---

## Responsive (si nécessaire)

```
1920×1080  → Layout 4×4 décrit ci-dessus (référence)
1440×900   → Augmenter gap à gap-1.5, réduire padding p-2
1280×720   → 2 colonnes, scroll autorisé (dashboard mobile non prioritaire)
< 768px    → Non supporté (app desktop uniquement)
```

---

## Checklist Implémentation

### Setup
- [ ] `h-[calc(100vh-56px)]` sur container dashboard
- [ ] `grid-rows-[56px_192px_192px_192px]` défini
- [ ] `overflow-hidden` sur container (pas de scroll)

### Widgets Row 1
- [ ] KPICard × 4 — `col-span-3 h-14`

### Widgets Row 2
- [ ] CashflowChart — `col-span-3 h-48` AreaChart vert
- [ ] PatrimoineChart — `col-span-3 h-48` LineChart bleu
- [ ] SCIOverview — `col-span-3 h-48` grid 3 mini-cards
- [ ] Top5Biens — `col-span-3 row-span-3 h-full` scrollable

### Widgets Row 3
- [ ] TransactionsTable — `col-span-9 h-48` max 7 lignes

### Widgets Row 4
- [ ] SimulationForm — `col-span-3 h-48` calcul live
- [ ] OpportunitesWidget — `col-span-3 h-48` top 2
- [ ] LocatairesCards — `col-span-3 h-48` top 4

### Tests
- [ ] Screenshot 1920×1080 — aucun scroll
- [ ] Top5Biens scroll interne fonctionne
- [ ] Aucun texte déborde de sa cellule (truncate partout)
- [ ] Recharts responsive sans déformer le layout

---

*Layout fixe. Pas de breakpoints complexes. 1 grille. 9 widgets. Production-ready.*
