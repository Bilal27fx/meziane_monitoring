# Meziane Monitoring

Plateforme de pilotage de patrimoine immobilier avec backend FastAPI, frontend Next.js, jobs asynchrones et documentation d'architecture.

## Vue d'ensemble

Le repository est organisé en trois blocs principaux:
- `backend/`: API, modèles, services métier, tâches asynchrones, stockage et authentification.
- `frontend/`: dashboard, espace agent et back-office admin.
- `docs/`: documentation active, historique des décisions et journal des refactors.

## Démarrage local

### 1. Infrastructure

```bash
docker-compose up -d
```

Services exposés:
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- MinIO API: `localhost:9000`
- MinIO Console: `localhost:9001`

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

API:
- base: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Application:
- web: `http://localhost:3000`

## Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Celery

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- TanStack Query
- Zustand

### Infra et outillage
- Docker Compose
- PostgreSQL 15
- Redis 7
- MinIO
- GitNexus pour l'analyse du code et l'impact avant modification

## Documentation

Point d'entrée recommandé:
- `CLAUDE.md`: cadre de travail, règles GitNexus et conventions du projet.
- `docs/README.md`: index documentaire et hiérarchie des documents.

Documents actifs à lire en priorité:
- `docs/architecture/PROFIL_ET_OBJECTIFS.md`
- `docs/architecture/ARCHITECTURE_SYSTEME.md`
- `docs/architecture/FRONTEND_ARCHITECTURE.md`
- `docs/PLAN.md`
- `docs/TRACKING.md`

Standard documentaire:
- `docs/DOCUMENTATION_STANDARDS.md`: conventions de structure, nommage et maintenance de la documentation.

## Structure

```text
meziane_monitoring/
├── backend/
├── frontend/
├── docs/
├── docker-compose.yml
├── Dockerfile.gitnexus
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

## Commandes utiles

```bash
# Infra
docker-compose up -d
docker-compose logs -f
docker-compose down

# Backend
cd backend
alembic upgrade head
uvicorn app.main:app --reload
pytest

# Frontend
cd frontend
npm run dev
npm run build

# GitNexus
cat .gitnexus/meta.json
npx gitnexus status
npx gitnexus analyze
```

## Règles de maintenance documentaire

- Les docs d'entrée ne doivent jamais pointer vers des chemins absolus ou obsolètes.
- `docs/architecture/` contient la documentation active et stable.
- `docs/history/` contient des archives et ne constitue pas la source de vérité par défaut.
- `docs/refactors/` trace les changements livrés et les RFC.
- Toute évolution notable du comportement, de l'architecture ou du workflow doit mettre à jour la doc correspondante.
