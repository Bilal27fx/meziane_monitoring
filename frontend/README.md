# Frontend - Meziane Monitoring

Application Next.js du projet Meziane Monitoring.

## Rôle

Le frontend expose trois surfaces principales:
- `dashboard`: vue synthétique patrimoine, cashflow, locataires et opportunités
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

## Démarrage

```bash
npm install
npm run dev
```

Application:
- web: `http://localhost:3000`

## Configuration

Variable principale:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Le frontend suppose qu'une API FastAPI compatible tourne sur cette URL.

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

## Conventions utiles

- Le fetching passe principalement par `lib/hooks/`.
- Le client HTTP central est `lib/api/client.ts`.
- L'état UI partagé utilise `lib/stores/app-store.ts`.
- Les composants métier sont regroupés par zone fonctionnelle dans `components/`.

## Documentation liée

- `AGENTS.md`: contraintes spécifiques au frontend
- `CLAUDE.md`: consignes de travail locales
- `../docs/architecture/FRONTEND_ARCHITECTURE.md`: architecture cible du frontend

## Points d'attention

- La version de Next.js peut diverger de conventions plus anciennes; lire `AGENTS.md` avant une modification majeure.
- Si le comportement réel diverge de la doc d'architecture, documenter l'écart plutôt que le masquer.
