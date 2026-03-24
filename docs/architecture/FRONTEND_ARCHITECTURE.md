# Frontend Architecture — Meziane Monitoring
**Version 3.0 — 23 mars 2026**
**3 pages : Dashboard · Agent · Admin**

---

## 1. Vision

**Bloomberg Terminal × Perplexity Finance**

- Interface **ultra-dense** : toutes les données critiques sur 1 écran, zéro scroll
- Dark mode permanent (`#0a0a0a`) — pas de toggle, pas de light mode
- Données **live** via polling React Query (30s) + WebSocket pour alertes critiques
- **3 pages uniquement** — pas de navigation complexe, tout accessible en 1 clic
- Chaque page est **autonome** : tabs internes pour naviguer entre les vues

---

## 2. Stack Technique

```
Next.js 14 (App Router)
TypeScript 5.3
TailwindCSS 3.4
shadcn/ui (composants primitifs)
Recharts 2.x (charts — léger, performant)
TanStack Query v5 (data fetching + cache)
Zustand (UI state — tabs, modals, filters)
next-themes (dark mode permanent)
```

Pas de Redux. Pas de GraphQL. Pas de Prisma côté front. KISS.

---

## 3. Structure des 3 Pages

```
/login                     → Auth (page isolée)
/(app)/dashboard           → Bloomberg dashboard (page principale)
/(app)/agent               → Centre de contrôle agents IA
/(app)/admin               → Back-office complet (CRUD + config)
```

### Routing App Router

```
src/app/
├── (auth)/
│   └── login/
│       └── page.tsx
└── (app)/
    ├── layout.tsx          ← Sidebar + Header partagés
    ├── dashboard/
    │   └── page.tsx
    ├── agent/
    │   └── page.tsx
    └── admin/
        └── page.tsx
```

---

## 4. Layout Global — Sidebar + Header

### Sidebar (48px de large — icônes uniquement)

```
┌────┐
│ M  │  ← Logo Meziane (16px, font-semibold)
├────┤
│ ▤  │  ← Dashboard (icône Grid)
│ ⚡  │  ← Agent (icône Zap)
│ ⚙  │  ← Admin (icône Settings)
├────┤
│    │
│    │  (espace vide)
│    │
├────┤
│ B  │  ← Avatar Bilal (initiales)
└────┘
```

```tsx
// Sidebar : w-12 (48px), h-screen, fixed
// Background : bg-[#0d0d0d] border-r border-neutral-800
// Icons : text-neutral-500 hover:text-white hover:bg-neutral-800 rounded-md
// Active : text-white bg-neutral-800
// Transitions : transition-colors duration-100
```

### Header (56px de haut, sur les 3 pages)

```
┌─────────────────────────────────────────────────────────────────┐
│ [Nom page]     │ [Status API] [Status Celery]  │ [heure] [date] │
└─────────────────────────────────────────────────────────────────┘
```

```tsx
// Header : h-14, bg-[#0d0d0d] border-b border-neutral-800
// Gauche : Titre de page (text-sm font-medium text-white)
// Centre : StatusBadge API (vert/rouge) + StatusBadge Celery
// Droite : Horloge live (font-mono text-xs text-neutral-400) + date
```

### StatusBadge Component

```tsx
interface StatusBadgeProps {
  label: string   // "API" | "Celery" | "Bridge"
  status: "ok" | "error" | "warning"
}
// Design : dot coloré (2px) + label text-[10px] font-mono
// ok → dot bg-green-500 text-neutral-400
// error → dot bg-red-500 text-red-400 (pulse animation)
// warning → dot bg-yellow-500 text-yellow-400
```

---

## 5. Page — Dashboard

**Objectif : tout visible sur 1920×1080 sans scroll**
**Voir DASHBOARD_LAYOUT_PLAN.md pour le layout exact pixel par pixel**

### Widgets (9 au total)

| Widget | Colonnes | Lignes | Hauteur |
|--------|----------|--------|---------|
| KPICard × 4 | 3 chacun | 1 | 56px |
| CashflowChart | 3 | 1 | 192px |
| PatrimoineChart | 3 | 1 | 192px |
| SCIOverview | 3 | 1 | 192px |
| Top5Biens | 3 | 3 | 576px |
| TransactionsTable | 9 | 1 | 192px |
| SimulationForm | 3 | 1 | 192px |
| OpportunitesWidget | 3 | 1 | 192px |
| LocatairesCards | 3 | 1 | 192px |

### KPICard

```tsx
interface KPICardProps {
  title: string
  value: string        // "2.4M€" | "+18.5%"
  change?: number      // +3.2 ou -1.4
  trend?: "up" | "down" | "neutral"
  subtitle?: string    // "Mois en cours"
  icon?: LucideIcon
}

// Design :
// Container : h-14 p-2 bg-[#111111] border border-neutral-800 rounded-md
// Title : text-[10px] text-neutral-500 font-medium uppercase tracking-wide
// Value : text-base font-semibold font-mono text-white tabular-nums
// Change : text-[10px] font-mono
//   trend up   → text-green-500 "▲ +3.2%"
//   trend down → text-red-500   "▼ -1.4%"
```

### CashflowChart / PatrimoineChart

```tsx
// Recharts AreaChart / LineChart
// Container : h-48 p-2 bg-[#111111] border border-neutral-800 rounded-md
// Chart : h-36 (laisse 12px header + 36px chart header)
// Axes : fontSize={8} stroke="#525252" (neutral-600)
// Grid : strokeDasharray="2 2" stroke="#262626" (neutral-800)
// Tooltip : bg-[#1a1a1a] border-neutral-700 text-xs font-mono
// CashflowChart :
//   Area fill="#22c55e" fillOpacity=0.12 stroke="#22c55e" strokeWidth=1.5
// PatrimoineChart :
//   Line stroke="#3b82f6" strokeWidth=1.5 dot={false}
```

### SCIOverview

```tsx
// Grid 3x2 de mini-cards dans le widget h-48
// Chaque mini-card : bg-[#0d0d0d] border border-neutral-800 rounded p-1.5
// Nom SCI : text-[10px] text-neutral-400 font-medium truncate
// Valeur principale : text-xs text-white font-mono font-semibold
// Sous-label : text-[9px] text-neutral-600
// Indicateur cashflow : vert si > 0, rouge si < 0
```

### Top5Biens (row-span-3)

```tsx
// Container : h-full p-2 bg-[#111111] border border-neutral-800 rounded-md
// Header : Titre + badge "YTD 2026"
// Liste scrollable des 5 biens
// Chaque item :
//   Rang : text-[10px] text-neutral-600 font-mono w-4
//   Adresse : text-xs text-white truncate max-w-[160px]
//   TRI : text-xs font-mono text-green-500 (si > 5%) / yellow (3-5%) / red (< 3%)
//   Bar : bg-green-500/20 relative width proportionnelle au TRI
//   Sparkline cashflow mensuel (5 derniers mois, 30px de large)
```

### TransactionsTable (col-span-9)

```tsx
// Container : h-48 p-2 bg-[#111111] border border-neutral-800 rounded-md
// Table : text-[10px] font-mono
// Header : text-[9px] text-neutral-600 uppercase tracking-widest border-b border-neutral-800
// Colonnes : Date | Type | Description | Catégorie | SCI | Montant | Statut
// Max 7 lignes visibles
// Montant : text-green-500 si > 0, text-red-500 si < 0
// Badge catégorie : bg-neutral-800 text-neutral-300 text-[9px] px-1 rounded
// Badge statut : pill coloré (validé → green, attente → yellow, rejeté → red)
// Hover row : bg-neutral-900 cursor-pointer
```

### SimulationForm

```tsx
// Container : h-48 p-2 bg-[#111111] border border-neutral-800 rounded-md
// Formulaire inline compact :
//   3 inputs : Prix (€), Apport (€), Taux (%)
//   Input : h-7 text-xs font-mono bg-[#0d0d0d] border-neutral-800
//   Label : text-[9px] text-neutral-600 uppercase
// Résultat live (calcul côté client, pas d'API) :
//   TRI brut : text-sm font-mono font-bold text-green-500
//   TRI net : text-xs font-mono text-green-400
//   Cashflow mensuel net : text-xs font-mono
//   Mensualité : text-xs font-mono text-neutral-400
// Bouton : text-[10px] h-6 bg-neutral-800 hover:bg-neutral-700
```

### OpportunitesWidget

```tsx
// Container : h-48 p-2 bg-[#111111] border border-neutral-800 rounded-md
// Header : "Opportunités IA" + badge nb nouvelles (bg-green-500/20 text-green-400)
// Max 2 opportunités affichées
// Chaque opportunité :
//   Score global : cercle coloré text-xs font-mono font-bold
//   Adresse + ville : text-xs text-white
//   Prix : text-xs font-mono
//   TRI estimé : text-xs text-green-500 font-mono
//   Tags : DPE, nb pièces, surface — text-[9px] bg-neutral-800 px-1 rounded
// Footer : lien "Voir tous →" vers page Agent
```

### LocatairesCards

```tsx
// Container : h-48 p-2 bg-[#111111] border border-neutral-800 rounded-md
// Header : "Locataires" + badge nb actifs
// Max 4 locataires
// Chaque locataire :
//   Nom : text-xs text-white
//   Bien : text-[9px] text-neutral-500 truncate
//   Loyer : text-xs font-mono text-neutral-300
//   Statut paiement :
//     OK → dot bg-green-500 + "À jour"
//     Retard → dot bg-yellow-500 + "J+X"
//     Impayé → dot bg-red-500 pulse + "IMPAYÉ" (text-red-400 font-semibold)
```

---

## 6. Page — Agent

**Une page, 3 onglets internes : Prospection · Tâches · Logs**

### Layout Agent

```
┌──────────────────────────────────────────────────────────────────────┐
│ AGENT CONTROL CENTER           [Prospection] [Tâches] [Logs]         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  [ONGLET PROSPECTION ACTIF PAR DÉFAUT]                               │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### Onglet Prospection

```
┌──────────────────────────────────────┬────────────────────────────────┐
│ AGENT PROSPECTION                    │ OPPORTUNITÉS (filtres actifs)  │
│ Status : ● Actif                     │ [Toutes] [Nouveau] [Vu] [Score]│
│ Dernière exécution : il y a 2h      ├────────────────────────────────┤
│ Prochain run : dans 4h              │ ┌────────────────────────────┐ │
│                                      │ │ Score: 92 │ Paris 18e      │ │
│ CONFIGURATION                        │ │ 485 000€  │ 52m²  2P      │ │
│ ─────────────────                    │ │ TRI: 7.8% │ DPE: C        │ │
│ Villes cibles                        │ │ [VU] [ANALYSER] [REJETER] │ │
│ [Paris ×] [Lyon ×] [+Ajouter]       │ └────────────────────────────┘ │
│                                      │ ┌────────────────────────────┐ │
│ Budget max                           │ │ Score: 87 │ Lyon 3e        │ │
│ [████████░░] 600 000 €              │ │ 320 000€  │ 68m²  3P      │ │
│                                      │ │ TRI: 8.2% │ DPE: B        │ │
│ TRI minimum                          │ │ [NOUVEAU] [ANALYSER] [REJ]│ │
│ [████░░░░░░] 6%                     │ └────────────────────────────┘ │
│                                      │ ┌────────────────────────────┐ │
│ Surface min                          │ │ Score: 74 │ Paris 15e      │ │
│ [██░░░░░░░░] 30 m²                  │ │ 290 000€  │ 31m²  1P      │ │
│                                      │ │ TRI: 6.1% │ DPE: D        │ │
│ Sources actives                      │ │ [NOUVEAU] [ANALYSER] [REJ]│ │
│ [✓ SeLoger] [✓ PAP] [✗ LBC]        │ └────────────────────────────┘ │
│                                      │                                │
│ [LANCER MAINTENANT]                  │ [Charger plus (12 restantes)]  │
│ [SAUVEGARDER CONFIG]                 │                                │
└──────────────────────────────────────┴────────────────────────────────┘
```

**Spécifications Prospection :**

```tsx
// Layout : grid grid-cols-12 gap-2
// Panneau gauche : col-span-4, panneau configuration
// Panneau droite : col-span-8, liste opportunités

// Carte Opportunité :
// bg-[#111111] border border-neutral-800 rounded-md p-3
// Score badge : rounded-full w-10 h-10 flex items-center justify-center
//   Score > 85 → bg-green-500/20 text-green-400 border border-green-500/30
//   Score 70-85 → bg-yellow-500/20 text-yellow-400 border border-yellow-500/30
//   Score < 70 → bg-red-500/20 text-red-400 border border-red-500/30

// Bouton ANALYSER → ouvre Modal Analyse détaillée
// Modal Analyse : overlay dark, risques IA, simulation acquisition, comparaison marché
```

### Onglet Tâches

```
CELERY TASKS — ÉTAT EN TEMPS RÉEL

┌─────────────────────┬───────────┬────────────────┬──────────────┬─────────┐
│ Task                │ Statut    │ Dernière exec  │ Prochaine    │ Actions │
├─────────────────────┼───────────┼────────────────┼──────────────┼─────────┤
│ sync_banking        │ ● OK      │ 15/03 14:32    │ Manuel       │ ▶ Lancer│
│ run_prospection     │ ● OK      │ 23/03 06:00    │ 24/03 06:00  │ ▶ Lancer│
│ generate_quittances │ ● OK      │ 01/03 08:00    │ 01/04 08:00  │ ▶ Lancer│
│ send_alerte_impayes │ ⚠ Warning │ 18/03 09:00    │ 25/03 09:00  │ ▶ Lancer│
└─────────────────────┴───────────┴────────────────┴──────────────┴─────────┘

STATS CELERY
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Tasks/24h    │ Succès       │ Erreurs      │ En attente   │
│     12       │ 11 (91.7%)   │ 1            │ 0            │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**Spécifications Tâches :**

```tsx
// GET /api/dashboard/global → stats plugins
// Statuts récupérés via polling (10s) sur endpoint Celery (à créer) ou Redis
// Bouton "Lancer" → POST /api/tasks/{task_name}/trigger
// Statut : dot coloré + texte
//   OK → green-500
//   Warning → yellow-500
//   Error → red-500 pulse
```

### Onglet Logs

```
LOGS EN TEMPS RÉEL

[Filtres : Tous ▼] [Agent ▼] [Niveau: INFO ▼]        [● Live]

23/03 14:32:01  INFO   [prospection]  Scan SeLoger Paris 18e — 47 annonces trouvées
23/03 14:32:03  INFO   [prospection]  3 nouvelles opportunités scorées (>70)
23/03 14:31:58  DEBUG  [banking]      Sync compte FR76... — 0 nouvelle transaction
23/03 14:30:12  WARN   [quittances]   Locataire Martin — quittance mars non payée
23/03 14:29:45  INFO   [auth]         Login user bilal@meziane.fr
23/03 14:15:00  INFO   [celery]       Task run_prospection_agent_task SUCCESS (3.2s)
...
```

**Spécifications Logs :**

```tsx
// WebSocket ws://api/ws/logs ou polling 5s GET /api/logs?limit=50
// Affichage monospace text-[10px] font-mono
// Color coding :
//   INFO  → text-neutral-400
//   DEBUG → text-neutral-600
//   WARN  → text-yellow-500
//   ERROR → text-red-500
// Live indicator : dot vert pulse si connexion WS active
// Auto-scroll vers le bas (derniers logs)
// Max 200 lignes affichées (virtualisation)
```

---

## 7. Page — Admin

**Une page, 5 onglets : SCI · Biens · Locataires · Transactions · Système**

### Layout Admin

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ADMINISTRATION     [SCI] [Biens] [Locataires] [Transactions] [Système]   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  [ONGLET ACTIF]                                                           │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### Onglet SCI

```
GESTION SCI                                              [+ Créer une SCI]

┌──────────┬────────────┬──────────┬──────────┬────────────┬──────────────┐
│ Nom      │ SIRET      │ Nb Biens │ Valeur   │ Cashflow   │ Actions      │
├──────────┼────────────┼──────────┼──────────┼────────────┼──────────────┤
│ SCI Fach │ 892 456 .. │ 2        │ 680 000€ │ +2 300€/m │ [✏️] [🗑️]   │
│ La Rena. │ 901 234 .. │ 1        │ 120 000€ │ +3 000€/m │ [✏️] [🗑️]   │
│ [Nom]    │ 456 789 .. │ 1        │ N/A      │ +3 000€/m │ [✏️] [🗑️]   │
└──────────┴────────────┴──────────┴──────────┴────────────┴──────────────┘

[← ← 1/1 → →]  3 résultats
```

**Modal Créer/Modifier SCI :**
```
┌──────────────────────────────────────────────────────┐
│ CRÉER UNE SCI                                  [✕]   │
├──────────────────────────────────────────────────────┤
│ Nom *              [                          ]       │
│ SIRET              [                          ]       │
│ Forme juridique    [SCI ▼                     ]       │
│ Capital social (€) [                          ]       │
│ Adresse siège      [                          ]       │
│ Date création      [  /  /    ]                       │
│ Email de contact   [                          ]       │
├──────────────────────────────────────────────────────┤
│                        [Annuler] [Créer la SCI]       │
└──────────────────────────────────────────────────────┘
```

### Onglet Biens

```
GESTION BIENS             [Filtrer : Toutes SCI ▼] [Tous statuts ▼]  [+ Ajouter]

┌────────────────┬────────┬───────┬────────┬────────┬─────────┬──────────────┐
│ Adresse        │ SCI    │ Type  │ Valeur │ Loyer  │ TRI Net │ Actions      │
├────────────────┼────────┼───────┼────────┼────────┼─────────┼──────────────┤
│ 42 av Victor.  │ Facha  │ Appt  │ 350K€  │ 1450€  │ 4.8%   │ [✏️][🗑️][📄]│
│ Studio 18e     │ Facha  │ Studio│ 280K€  │ 850€   │ 3.5%   │ [✏️][🗑️][📄]│
│ Local comm. 18 │ Renas. │ Local │ 120K€  │ 3000€  │ 28.0%  │ [✏️][🗑️][📄]│
│ Hôtel Bordeaux │ [Nom]  │ Hôtel │ N/A    │ 3000€  │ —      │ [✏️][🗑️][📄]│
└────────────────┴────────┴───────┴────────┴────────┴─────────┴──────────────┘

[← ← 1/1 → →]  4 résultats   Valeur totale : 750 000 €
```

**Modal Créer/Modifier Bien :**
```
┌─────────────────────────────────────────────────────────────────┐
│ AJOUTER UN BIEN                                           [✕]   │
├─────────────────────────────────────────────────────────────────┤
│ LOCALISATION                                                     │
│ SCI *              [Facha ▼                               ]      │
│ Adresse *          [                                      ]      │
│ Complément         [                                      ]      │
│ Ville *            [            ]  Code postal * [       ]      │
├─────────────────────────────────────────────────────────────────┤
│ CARACTÉRISTIQUES                                                 │
│ Type *             [Appartement ▼]  Surface (m²) [      ]       │
│ Nb pièces          [     ]          Étage        [      ]       │
│ DPE                [A ▼]            Validité DPE [  /  /  ]     │
├─────────────────────────────────────────────────────────────────┤
│ FINANCIER                                                        │
│ Prix acquisition * [              ]  Date acquisition [      ]  │
│ Valeur actuelle    [              ]  Statut [Loué ▼]            │
├─────────────────────────────────────────────────────────────────┤
│                         [Annuler]  [Enregistrer le bien]        │
└─────────────────────────────────────────────────────────────────┘
```

**Bouton 📄 → Panneau documents** (s'ouvre à droite) :
```
Checklist documents locataire/bien (DPE, titre propriété, contrat assurance...)
Upload zone drag & drop
Liste fichiers existants avec téléchargement
```

### Onglet Locataires

```
GESTION LOCATAIRES             [Statut paiement ▼]  [SCI ▼]     [+ Ajouter]

┌───────────────┬─────────┬──────────────────┬────────┬──────────┬──────────┐
│ Locataire     │ Bien    │ Bail             │ Loyer  │ Paiement │ Actions  │
├───────────────┼─────────┼──────────────────┼────────┼──────────┼──────────┤
│ Jean Dupont   │ 42 av V │ 01/01/24→31/12/24│ 1 450€ │ ● À jour │[✏️][📋][💬]│
│ Marie Martin  │ Studio  │ 01/03/25→28/02/26│ 850€   │ ⚠ J+8   │[✏️][📋][💬]│
└───────────────┴─────────┴──────────────────┴────────┴──────────┴──────────┘

[← ← 1/1 → →]  2 résultats
```

**Modal Créer/Modifier Locataire :**
```
┌─────────────────────────────────────────────────────────────────┐
│ AJOUTER UN LOCATAIRE                                      [✕]   │
├─────────────────────────────────────────────────────────────────┤
│ IDENTITÉ                                                         │
│ Prénom *   [                 ]  Nom *     [                ]    │
│ Email *    [                              ]                      │
│ Téléphone  [                 ]  Naissance [  /  /    ]         │
│ Profession [                              ]                      │
│ Revenus annuels (€) [                   ]                        │
├─────────────────────────────────────────────────────────────────┤
│ BAIL                                                             │
│ Bien *         [42 av Victor Hugo ▼                      ]      │
│ Date début *   [  /  /    ]  Date fin     [  /  /    ]         │
│ Loyer (€) *    [         ]  Charges (€)   [         ]          │
│ Dépôt garantie [         ]  Révision      [IRL ▼    ]          │
├─────────────────────────────────────────────────────────────────┤
│ DOCUMENTS (optionnel)                                            │
│ [Glisser-déposer pièce identité, justificatifs de revenus...]   │
├─────────────────────────────────────────────────────────────────┤
│ [Annuler]  [Enregistrer le locataire]                           │
└─────────────────────────────────────────────────────────────────┘
```

**Bouton 📋 → Panneau Quittances** (s'ouvre à droite) :
```
Liste 12 derniers mois : [Mois] [Montant] [Statut] [Télécharger PDF]
Bouton "Générer quittance" → POST /api/tasks/generate_quittances_task
```

**Bouton 💬 → Panneau Communication** :
```
Historique alertes envoyées (email/WhatsApp)
Bouton "Envoyer rappel loyer" → API notif
```

### Onglet Transactions

```
TRANSACTIONS          [SCI ▼] [Catégorie ▼] [Statut ▼] [Date ▼]  [+ Ajouter]

┌────────┬──────┬───────────────────┬──────────────┬──────┬───────┬──────────┐
│ Date   │ SCI  │ Libellé           │ Catégorie    │ Bien │ Mont. │ Actions  │
├────────┼──────┼───────────────────┼──────────────┼──────┼───────┼──────────┤
│ 15/03  │Facha │ Loyer Mars Dupont │ 🏠 Loyer     │ 42av │+1450€│[✏️][✓][✗]│
│ 15/03  │Facha │ Loyer Mars Martin │ 🏠 Loyer     │ Stu. │+850€ │[✏️][✓][✗]│
│ 12/03  │Facha │ Répar. chaudière  │ 🔧 Travaux   │ 42av │ -650€│[✏️][✓][✗]│
│ 01/03  │Renas │ Loyer commercial  │ 🏠 Loyer     │ Loc. │+3000€│[✏️][✓][✗]│
└────────┴──────┴───────────────────┴──────────────┴──────┴───────┴──────────┘

TOTAUX (filtre actif) :  Revenus : +5 300€   Dépenses : -650€   Net : +4 650€
[← ← 1/4 → →]  38 résultats     [Exporter CSV]
```

**Spécifications Transactions :**
```tsx
// Pagination : 20 lignes/page (GET /api/transactions?limit=20&offset=0)
// Filtres combinables : sci_id, categorie, statut, date_debut, date_fin
// Bouton ✓ → valider transaction (PATCH /api/transactions/{id}/valider)
// Bouton ✗ → rejeter transaction (PATCH /api/transactions/{id}/rejeter)
// Bouton "Catégoriser IA" (en masse) → POST /api/transactions/categorize-batch
// Import bancaire : bouton "Sync Bridge" → POST /api/banking/sync
// Ligne cliquable → expand inline (notes, pièce jointe)
```

### Onglet Système

```
CONFIGURATION SYSTÈME

┌──────────────────────────────────┬──────────────────────────────────────┐
│ UTILISATEURS                     │ INTÉGRATIONS                          │
│                                  │                                       │
│ bilal@meziane.fr  Admin    [✏️]  │ Bridge API      ● Configuré    [Test]│
│                            [+]   │ Anthropic API   ● Configuré    [Test]│
│                                  │ OpenAI API      ● Configuré    [Test]│
│                                  │ SMTP Email      ⚠ Non config  [Setup]│
│                                  │ Twilio WhatsApp ⚠ Non config  [Setup]│
├──────────────────────────────────┼──────────────────────────────────────┤
│ VARIABLES ENVIRONNEMENT          │ INFRASTRUCTURE                        │
│                                  │                                       │
│ ALLOWED_ORIGINS  [Modifier]     │ PostgreSQL   ● Connecté               │
│ SECRET_KEY       [Régénérer]    │ Redis        ● Connecté               │
│ ENVIRONMENT      production      │ MinIO        ● Connecté               │
│                                  │ Celery Beat  ● Running                │
├──────────────────────────────────┼──────────────────────────────────────┤
│ DONNÉES                          │                                       │
│                                  │                                       │
│ [Exporter tout en CSV]           │                                       │
│ [Exporter tout en JSON]          │                                       │
│ [Vider cache Redis]              │                                       │
│ [Relancer index GitNexus]        │                                       │
└──────────────────────────────────┴──────────────────────────────────────┘
```

---

## 8. Page — Login

```
[Fond noir #0a0a0a]

          ┌──────────────────────────────────────┐
          │                                      │
          │     MEZIANE MONITORING               │
          │     ─────────────────               │
          │                                      │
          │     Email                            │
          │     [                              ] │
          │                                      │
          │     Mot de passe                     │
          │     [                              ] │
          │                                      │
          │     [    Se connecter →    ]         │
          │                                      │
          │     ─────────────────               │
          │     v1.0.0 · backend OK              │
          │                                      │
          └──────────────────────────────────────┘
```

```tsx
// Centré avec max-w-sm mx-auto
// Card : bg-[#111111] border border-neutral-800 rounded-lg p-8
// Titre : text-lg font-semibold text-white
// Inputs : bg-[#0d0d0d] border-neutral-800 h-9 text-sm
// Bouton : bg-white text-black hover:bg-neutral-200 h-9 text-sm font-medium
// POST /api/auth/login (form: email + password)
// Stocker access_token + refresh_token en httpOnly cookie ou localStorage
// Redirect → /dashboard après succès
```

---

## 9. Design System Complet

### Palette de couleurs

```css
/* Backgrounds */
--bg-base:    #0a0a0a   /* Fond application */
--bg-card:    #111111   /* Fond cartes/widgets */
--bg-overlay: #0d0d0d   /* Fond inputs, sidebar */
--bg-hover:   #1a1a1a   /* Hover sur éléments */
--bg-active:  #262626   /* Élément actif/sélectionné */

/* Borders */
--border-default: #262626   /* neutral-800 */
--border-hover:   #404040   /* neutral-700 */
--border-focus:   #525252   /* neutral-600 */

/* Text */
--text-primary:   #ffffff   /* Titres, valeurs importantes */
--text-secondary: #a3a3a3   /* neutral-400 — Labels */
--text-muted:     #737373   /* neutral-500 — Descriptions */
--text-faint:     #525252   /* neutral-600 — Placeholders */

/* Data */
--green:   #22c55e   /* Positif, revenus, OK */
--red:     #ef4444   /* Négatif, dépenses, erreur */
--blue:    #3b82f6   /* Info, neutre, lien */
--yellow:  #eab308   /* Warning, retard */
--purple:  #a855f7   /* Highlight spécial */

/* Opacités standard */
--green-bg:  rgba(34,197,94, 0.12)
--red-bg:    rgba(239,68,68, 0.12)
--blue-bg:   rgba(59,130,246, 0.12)
--yellow-bg: rgba(234,179,8, 0.12)
```

### Typographie

```css
/* Fonts */
--font-sans: 'Inter Variable', sans-serif     /* UI général */
--font-mono: 'JetBrains Mono', monospace      /* Chiffres, codes */

/* Scale (dense) */
text-[9px]  → 9px   /* Labels très compacts */
text-[10px] → 10px  /* Labels standards */
text-xs     → 12px  /* Corps de texte */
text-sm     → 14px  /* Titres secondaires */
text-base   → 16px  /* Valeurs KPI */
text-lg     → 18px  /* Valeurs importantes */

/* Chiffres financiers : TOUJOURS font-mono tabular-nums */
```

### Composants UI Réutilisables

```tsx
// Badge statut
<Badge variant="ok" | "warning" | "error" | "info" />
// Pill : rounded-full px-1.5 py-0.5 text-[9px] font-medium

// Tooltip
<Tooltip content="..." />
// bg-[#1a1a1a] border border-neutral-700 rounded text-xs p-2

// DataTable générique
<DataTable
  columns={[...]}
  data={[...]}
  pagination={true}
  pageSize={20}
  onRowClick={(row) => {}}
  loading={isLoading}
/>
// Header sticky, lignes hover:bg-neutral-900, border-b border-neutral-800/50

// Modal
<Modal title="..." open={open} onClose={() => {}} size="sm"|"md"|"lg">
// Overlay : bg-black/60 backdrop-blur-sm
// Card : bg-[#111111] border border-neutral-800

// ConfirmDialog
<ConfirmDialog
  title="Supprimer ce bien ?"
  description="Cette action est irréversible."
  onConfirm={() => {}}
/>
// Variant destructif : bouton rouge

// EmptyState
<EmptyState icon={...} title="..." description="..." action={...} />
// Pour tables vides ou erreurs API

// Skeleton loader
<Skeleton className="h-14 w-full" />
// bg-neutral-800/50 animate-pulse rounded
```

### Animations

```css
/* Seules animations autorisées */
transition-colors duration-100    /* Hover states */
animate-pulse                     /* Dot status erreur */
animate-spin                      /* Loading spinner (w-4 h-4) */

/* Pas de transitions complexes. Pas de slides. Pas de fades longs. */
```

---

## 10. API Client & Hooks

### Client Axios

```typescript
// lib/api/client.ts
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

// JWT interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh sur 401
api.interceptors.response.use(null, async (error) => {
  if (error.response?.status === 401) {
    const refreshed = await refreshToken()
    if (refreshed) return api.request(error.config)
    window.location.href = '/login'
  }
  return Promise.reject(error)
})
```

### Hooks React Query

```typescript
// lib/hooks/useDashboard.ts
export function useFullDashboard() {
  return useQuery({
    queryKey: ['dashboard', 'full'],
    queryFn: () => api.get('/api/dashboard/full').then(r => r.data),
    refetchInterval: 30_000,
    staleTime: 25_000,
  })
}

// lib/hooks/useAdmin.ts
export function useSCIs(params: { limit: number; offset: number }) {
  return useQuery({
    queryKey: ['sci', params],
    queryFn: () => api.get('/api/sci', { params }).then(r => r.data),
  })
}

export function useCreateSCI() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: SCICreate) => api.post('/api/sci', data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sci'] }),
  })
}

// Même pattern pour biens, locataires, transactions
```

### Zustand Store

```typescript
// lib/stores/app-store.ts
interface AppStore {
  // Navigation
  adminTab: 'sci' | 'biens' | 'locataires' | 'transactions' | 'systeme'
  agentTab: 'prospection' | 'taches' | 'logs'
  setAdminTab: (tab: AppStore['adminTab']) => void
  setAgentTab: (tab: AppStore['agentTab']) => void

  // Modals
  modal: { type: string; data?: unknown } | null
  openModal: (type: string, data?: unknown) => void
  closeModal: () => void

  // Filtres admin
  adminFilters: { sciId?: number; statut?: string; dateRange?: [Date, Date] }
  setAdminFilters: (f: Partial<AppStore['adminFilters']>) => void
}
```

---

## 11. Structure Dossiers

```
src/
├── app/
│   ├── (auth)/login/page.tsx
│   └── (app)/
│       ├── layout.tsx           ← Sidebar + Header
│       ├── dashboard/page.tsx
│       ├── agent/page.tsx
│       └── admin/page.tsx
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── StatusBadge.tsx
│   ├── dashboard/               ← Widgets du dashboard
│   │   ├── KPICard.tsx
│   │   ├── CashflowChart.tsx
│   │   ├── PatrimoineChart.tsx
│   │   ├── SCIOverview.tsx
│   │   ├── Top5Biens.tsx
│   │   ├── TransactionsTable.tsx
│   │   ├── SimulationForm.tsx
│   │   ├── OpportunitesWidget.tsx
│   │   └── LocatairesCards.tsx
│   ├── agent/                   ← Composants page Agent
│   │   ├── ProspectionPanel.tsx
│   │   ├── OpportuniteCard.tsx
│   │   ├── OpportuniteModal.tsx
│   │   ├── TasksTable.tsx
│   │   └── LogsViewer.tsx
│   ├── admin/                   ← Composants page Admin
│   │   ├── tabs/
│   │   │   ├── SCITab.tsx
│   │   │   ├── BiensTab.tsx
│   │   │   ├── LocatairesTab.tsx
│   │   │   ├── TransactionsTab.tsx
│   │   │   └── SystemTab.tsx
│   │   ├── forms/
│   │   │   ├── SCIForm.tsx
│   │   │   ├── BienForm.tsx
│   │   │   └── LocataireForm.tsx
│   │   └── panels/
│   │       ├── DocumentsPanel.tsx
│   │       ├── QuittancesPanel.tsx
│   │       └── CommunicationPanel.tsx
│   └── ui/                      ← Primitives shadcn + customs
│       ├── DataTable.tsx
│       ├── Modal.tsx
│       ├── ConfirmDialog.tsx
│       ├── Badge.tsx
│       ├── EmptyState.tsx
│       └── Skeleton.tsx
├── lib/
│   ├── api/
│   │   └── client.ts
│   ├── hooks/
│   │   ├── useDashboard.ts
│   │   ├── useAdmin.ts
│   │   ├── useAgent.ts
│   │   └── useAuth.ts
│   ├── stores/
│   │   └── app-store.ts
│   ├── types/
│   │   └── index.ts             ← Types générés depuis OpenAPI
│   └── utils/
│       ├── format.ts            ← formatCurrency, formatDate, formatPercent
│       └── calc.ts              ← TRI, cashflow net, mensualité
└── styles/
    └── globals.css
```

---

## 12. Roadmap

### Phase 1 — Foundation (2 jours)
- Init Next.js 14 + TypeScript + Tailwind + shadcn
- Layout Sidebar + Header + routing 3 pages
- Design system (couleurs, typo, composants UI de base)
- Page Login fonctionnelle (POST /api/auth/login)

### Phase 2 — Dashboard (2 jours)
- 9 widgets avec mock data statique
- Layout grid exact (DASHBOARD_LAYOUT_PLAN.md)
- Connexion API (React Query hooks)
- Refresh 30s

### Phase 3 — Page Agent (2 jours)
- Onglet Prospection (liste + config + modal analyse)
- Onglet Tâches (état Celery)
- Onglet Logs (viewer WebSocket)

### Phase 4 — Page Admin (3 jours)
- DataTable générique
- Onglets SCI, Biens, Locataires (CRUD complet)
- Onglet Transactions (filtres + validation)
- Onglet Système
- Panneaux latéraux (documents, quittances, communication)

### Phase 5 — Polish (1 jour)
- Loading states + Skeletons
- Error boundaries
- Toasts notifications (react-hot-toast)
- Types OpenAPI auto-générés

---

*3 pages. Zéro bloat. Production-ready.*
