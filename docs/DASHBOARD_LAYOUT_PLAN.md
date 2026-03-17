# Plan de Layout Dashboard - Meziane Monitoring

**Date:** 16 mars 2026
**Objectif:** Dashboard dense style Perplexity Finance, tout visible sur 1 écran sans scroll
**Résolution cible:** 1920x1080px

---

## 📐 Vue d'ensemble du Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│ Écran: 1920x1080 - Zone utile après header: ~1000px hauteur           │
├────────────────────────────────────────────────────────────────────────┤
│ LIGNE 1 (h-14 = 56px) - 4 KPI CARDS                                   │
├───────────────┬───────────────┬───────────────┬───────────────────────┤
│ Patrimoine    │ Cashflow      │ Alertes       │ Performance           │
│ 2.4M€         │ 12K€          │ 3             │ +18.5%                │
│ +3.20%        │               │               │ +18.50%               │
│ col-span-3    │ col-span-3    │ col-span-3    │ col-span-3            │
├───────────────┴───────────────┴───────────────┴───────────────────────┤
│ LIGNE 2 (h-48 = 192px) - 3 CHARTS + TOP5 DEBUT                        │
├───────────────┬───────────────┬───────────────┬───────────────────────┤
│ Cashflow 30j  │ Patrimoine    │ Aperçu SCI    │ Top 5 Biens          │
│ [AreaChart]   │ 12m           │ (6 mini-cards)│ (TRI)                │
│ Vert #22c55e  │ [LineChart]   │ SCI Paris: 2  │ #1 42 avenue...      │
│               │ Vert          │ SCI Lyon: 2   │   TRI: +9.2%         │
│               │               │ Revenus/CF    │ #2 8 boulevard...    │
│ col-span-3    │ col-span-3    │ col-span-3    │ col-span-3           │
│               │               │               │ row-span-3 ⬇️        │
├───────────────┴───────────────┴───────────────┤                       │
│ LIGNE 3 (h-48 = 192px) - TRANSACTIONS TABLE  │ #3 15 rue...         │
├───────────────────────────────────────────────┤   TRI: +8.5%         │
│ Transactions Récentes (Table complète)       │                       │
│ Date │ Type │ Description │ Catégorie │ Mont.│ #4 23 rue...         │
│ 15/03│ REV  │ Loyer Mars  │ Loyer     │ 1500€│   TRI: +8.1%         │
│ 15/03│ REV  │ Loyer Mars  │ Loyer     │ 2200€│                       │
│ 14/03│ DEP  │ Réparation  │ Mainten.  │ -450€│ #5 91 cours...       │
│ [6-7 lignes visibles]                         │   TRI: +7.8%         │
│ col-span-9                                    │                       │
├───────────────┬───────────────┬───────────────┤                       │
│ LIGNE 4 (h-48 = 192px)                        │ (fin Top5)           │
├───────────────┼───────────────┼───────────────┤                       │
│ Simulation    │ Opportunités  │ Locataires    │                       │
│ Acquisition   │ IA            │ Cards         │                       │
│ Prix: 250K€   │ • Lyon 3e     │ • J. Dupont   │                       │
│ Apport: 50K€  │   Score: 85   │   Paiement OK │                       │
│ → TRI: 8.2%   │ • Paris 15e   │ • M. Martin   │                       │
│               │   Score: 78   │   Retard 5j   │                       │
│ col-span-3    │ col-span-3    │ col-span-3    │ col-span-3           │
└───────────────┴───────────────┴───────────────┴───────────────────────┘
```

---

## 🎯 Structure Grid (grid-cols-12)

```tsx
<div className="grid grid-cols-12 gap-2">
  {/* ========== LIGNE 1: 4 KPI Cards ========== */}
  <div className="col-span-3">
    <KPICard title="Patrimoine Net" value="2.4M€" change={3.2} trend="up" />
  </div>
  <div className="col-span-3">
    <KPICard title="Cashflow Today" value="12K€" />
  </div>
  <div className="col-span-3">
    <KPICard title="Alertes IA" value="3" />
  </div>
  <div className="col-span-3">
    <KPICard title="Performance YTD" value="+18.5%" change={18.5} trend="up" />
  </div>

  {/* ========== LIGNE 2: Charts + SCI + Top5 début ========== */}
  <div className="col-span-3">
    <CashflowChart data={mockCashflowData} />
  </div>
  <div className="col-span-3">
    <PatrimoineChart data={mockPatrimoineData} />
  </div>
  <div className="col-span-3">
    <SCIOverview scis={mockSCIs} />
  </div>
  <div className="col-span-3 row-span-3">
    <Top5Biens biens={mockBiens} />
  </div>

  {/* ========== LIGNE 3: Transactions large ========== */}
  <div className="col-span-9">
    <TransactionsTable transactions={mockTransactions} />
  </div>
  {/* Top5Biens continue (row-span-3) */}

  {/* ========== LIGNE 4: Simulation + Opportunités + Locataires ========== */}
  <div className="col-span-3">
    <SimulationForm />
  </div>
  <div className="col-span-3">
    <OpportunitesWidget opportunites={mockOpportunites} />
  </div>
  <div className="col-span-3">
    <LocatairesCards locataires={mockLocataires} />
  </div>
  {/* Top5Biens se termine */}
</div>
```

---

## 📦 Dimensions précises par Widget

| Widget | Fichier | Hauteur | Colonnes | Lignes | Padding | Justification |
|--------|---------|---------|----------|--------|---------|---------------|
| **KPICard (x4)** | `KPICard.tsx` | `h-14` (56px) | 3 | 1 | `p-2` | Compact: titre + valeur + % |
| **CashflowChart** | `CashflowChart.tsx` | `h-48` (192px) | 3 | 1 | `p-2` | Graphique area + axes |
| **PatrimoineChart** | `PatrimoineChart.tsx` | `h-48` (192px) | 3 | 1 | `p-2` | Graphique line + axes |
| **SCIOverview** | `SCIOverview.tsx` | `h-48` (192px) | 3 | 1 | `p-2` | 6 mini-cards (grid 2x3) |
| **Top5Biens** | `Top5Biens.tsx` | `h-full` (~3×192px) | 3 | 3 | `p-2` | 5 biens détaillés, scrollable |
| **TransactionsTable** | `TransactionsTable.tsx` | `h-48` (192px) | 9 | 1 | `p-2` | Table large: 6-7 lignes |
| **SimulationForm** | `SimulationForm.tsx` | `h-48` (192px) | 3 | 1 | `p-2` | Form: 3 inputs + résultat |
| **OpportunitesWidget** | `OpportunitesWidget.tsx` | `h-48` (192px) | 3 | 1 | `p-2` | 2 opportunités compactes |
| **LocatairesCards** | `LocatairesCards.tsx` | `h-48` (192px) | 3 | 1 | `p-2` | 3-4 locataires compacts |

---

## 📏 Calcul total de la hauteur

```
Composant                   Hauteur
─────────────────────────────────────
Header (fixe):              56px
Padding top (p-3):          12px
─────────────────────────────────────
Ligne 1 - KPI Cards:        56px
Gap (gap-2):                 8px
─────────────────────────────────────
Ligne 2 - Charts/SCI:      192px
Gap:                         8px
─────────────────────────────────────
Ligne 3 - Transactions:    192px
Gap:                         8px
─────────────────────────────────────
Ligne 4 - Sim/Opp/Loc:     192px
Padding bottom (p-3):       12px
─────────────────────────────────────
TOTAL:                     736px ✅

Écran 1080p disponible:   1080px
Reste disponible:         ~344px
Marge de sécurité:        LARGE ✅
```

---

## 🎨 Design System - Perplexity Finance Style

### Couleurs

```css
/* Backgrounds */
--bg-main: #0d0d0d        /* Fond principal noir pur */
--bg-card: #121212        /* Fond des cartes */
--bg-hover: #262626       /* Hover state */

/* Borders */
--border-main: #262626    /* Bordures principales (neutral-800) */
--border-hover: #404040   /* Bordures hover (neutral-700) */

/* Text */
--text-primary: #ffffff   /* Texte principal blanc */
--text-secondary: #a3a3a3 /* Labels (neutral-400) */
--text-muted: #737373     /* Texte désactivé (neutral-500) */

/* Data Colors */
--color-positive: #22c55e /* Vert (green-500) - valeurs positives */
--color-negative: #ef4444 /* Rouge (red-500) - valeurs négatives */
--color-neutral: #3b82f6  /* Bleu (blue-500) - infos neutres */
--color-warning: #eab308  /* Jaune (yellow-500) - avertissements */
```

### Typographie

```css
/* Font Families */
font-sans: Inter Variable
font-mono: JetBrains Mono (pour chiffres)

/* Font Sizes */
text-[10px]: Labels, descriptions       (10px)
text-xs:     Titres secondaires         (12px)
text-sm:     Texte normal               (14px)
text-base:   Valeurs KPI                (16px)
text-lg:     Valeurs importantes        (18px)

/* Font Weights */
font-medium:   500 (labels)
font-semibold: 600 (valeurs)
font-bold:     700 (highlights)
```

### Espacements

```css
/* Padding */
p-2:   8px  (widgets standards)
p-2.5: 10px (alternative)
p-3:   12px (container principal)

/* Gaps */
gap-1:   4px  (éléments très proches)
gap-1.5: 6px  (éléments proches)
gap-2:   8px  (grille principale)
gap-3:   12px (sections)

/* Heights */
h-14: 56px  (KPI cards)
h-48: 192px (widgets standards)
h-full: auto (Top5Biens)
```

---

## 🔧 Modifications requises par Widget

### 1. KPICard.tsx ✅ DÉJÀ FAIT
```tsx
className="p-2 bg-[#121212] border-neutral-800 h-14"
title: text-[10px]
value: text-base (16px)
trend: text-[10px], icons h-2.5 w-2.5
```

### 2. CashflowChart.tsx ✅ DÉJÀ FAIT
```tsx
className="p-2 bg-[#121212] border-neutral-800 h-48"
chart height: h-36 (144px)
title: text-xs
subtitle: text-[10px]
axes fontSize: 8
```

### 3. PatrimoineChart.tsx ⚠️ À MODIFIER
**Changements nécessaires:**
- Classe: Ajouter `h-48` à la Card
- Chart div: Changer de `h-36` à `h-36` (garder)
- Titre: "Évolution Patrimoine 12m" → "Patrimoine 12m"

### 4. SCIOverview.tsx ⚠️ À MODIFIER
**Changements nécessaires:**
- Classe: Ajouter `h-48` à la Card
- Padding: `p-4` → `p-2`
- Mini-cards: Grid 2x3, ultra-compacts
- Titre: `text-sm` → `text-xs`
- Labels: `text-xs` → `text-[10px]`
- Valeurs: `text-sm` → `text-xs`

### 5. Top5Biens.tsx ⚠️ À MODIFIER
**Changements nécessaires:**
- Classe: Remplacer `h-[25rem]` par `h-full` pour occuper 3 lignes
- Padding: Garder `p-2`
- Scrollable: Garder `overflow-y-auto`
- Cards: Garder compact actuel

### 6. TransactionsTable.tsx ⚠️ À MODIFIER
**Changements nécessaires:**
- Classe: Ajouter `h-48` à la Card
- Padding: `p-4` → `p-2`
- Limiter à 6-7 lignes max
- Headers: `text-sm` → `text-xs`
- Cells: `text-sm` → `text-[10px]`
- Row padding: Réduire au minimum

### 7. LocatairesCards.tsx ⚠️ À MODIFIER
**Changements nécessaires:**
- Classe: Ajouter `h-48` à la Card
- Padding: `p-4` → `p-2`
- Cards: Max 3-4 locataires compacts
- Titre: `text-sm` → `text-xs`
- Noms: `text-sm` → `text-xs`
- Status: `text-xs` → `text-[10px]`

### 8. SimulationForm.tsx ⚠️ À MODIFIER
**Changements nécessaires:**
- Classe: Ajouter `h-48` à la Card
- Padding: `p-4` → `p-2`
- Input heights: Réduire
- Labels: `text-sm` → `text-xs`
- Inputs: Hauteur réduite
- Résultat: Compact

### 9. OpportunitesWidget.tsx ⚠️ À MODIFIER
**Changements nécessaires:**
- Classe: Ajouter `h-48` à la Card
- Padding: `p-4` → `p-2`
- Max 2 opportunités
- Cards: Très compacts
- Titre: `text-sm` → `text-xs`
- Score badge: Plus petit
- Metrics: `text-xs` → `text-[10px]`

---

## ✅ Checklist d'implémentation

### Phase 1: Layout principal
- [ ] Modifier `dashboard/page.tsx` avec nouvelle structure grid
- [ ] Vérifier que Top5Biens utilise `row-span-3`
- [ ] Vérifier que TransactionsTable utilise `col-span-9`

### Phase 2: Widgets à modifier
- [x] KPICard - Déjà fait
- [x] CashflowChart - Déjà fait
- [ ] PatrimoineChart - Ajouter h-48
- [ ] SCIOverview - Réduire tailles + h-48
- [ ] Top5Biens - h-full au lieu de h-[25rem]
- [ ] TransactionsTable - h-48 + réduire tailles
- [ ] LocatairesCards - h-48 + compact
- [ ] SimulationForm - h-48 + compact
- [ ] OpportunitesWidget - h-48 + compact

### Phase 3: Tests
- [ ] Tester sur 1920x1080 - tout visible sans scroll
- [ ] Vérifier que Top5Biens scroll correctement
- [ ] Vérifier alignement grid
- [ ] Vérifier responsive (si temps)

---

## 🎯 Résultat attendu

**Dashboard professionnel style Perplexity Finance:**
- ✅ Tout visible sur 1 écran sans scroll
- ✅ Design épuré, noir #0d0d0d
- ✅ Widgets compacts mais lisibles
- ✅ Pas d'espace vide inutile
- ✅ Hiérarchie visuelle claire
- ✅ Performance optimale

---

**Document de référence pour l'implémentation**
**À suivre étape par étape**
