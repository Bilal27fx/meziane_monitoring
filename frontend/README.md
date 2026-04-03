# Frontend - Meziane Monitoring

Frontend Next.js du projet Meziane Monitoring.

## Rôle

Cette application expose trois surfaces principales:
- `dashboard`: vue synthétique patrimoine, cashflow, locataires, opportunités
- `agent`: centre de contrôle des agents et tâches IA
- `admin`: back-office de gestion SCI, biens, locataires, transactions et système

## Stack

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- TanStack Query
- Zustand
- Axios

## Structure

```text
frontend/
├── app/
│   ├── (auth)/
│   └── (app)/
├── components/
│   ├── admin/
│   ├── agent/
│   ├── dashboard/
│   ├── layout/
│   └── ui/
├── lib/
│   ├── api/
│   ├── hooks/
│   ├── stores/
│   ├── types/
│   └── utils/
└── public/
```

## Lancement

```bash
npm install
npm run dev
```

Application disponible sur `http://localhost:3000`.

## Configuration

Variable principale:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Le frontend suppose qu'une API FastAPI compatible tourne sur cette URL.

## Conventions utiles

- Le fetching passe principalement par `lib/hooks/`.
- Le client HTTP central est `lib/api/client.ts`.
- L'état UI partagé utilise `lib/stores/app-store.ts`.
- Les composants métier sont regroupés par zone fonctionnelle dans `components/`.

## Points d'attention

- Lire `AGENTS.md` avant toute modification majeure: la version de Next.js utilisée peut diverger des conventions historiques.
- L'architecture cible est décrite dans `../docs/architecture/FRONTEND_ARCHITECTURE.md`.
- Si le comportement réel diverge de la doc d'architecture, documenter l'écart plutôt que le masquer.
