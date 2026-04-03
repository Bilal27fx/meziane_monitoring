# Meziane Monitoring

Plateforme de pilotage de patrimoine immobilier avec backend FastAPI, dashboard Next.js, jobs asynchrones et documentation d'architecture.

## Vue rapide

Le repo est organisé en trois blocs:
- `backend/`: API, modèles, services métier, tâches Celery, stockage et auth.
- `frontend/`: dashboard, espace agent, back-office admin.
- `docs/`: architecture, suivi des RFC, historique, refactors livrés.

## Démarrage

### 1. Infrastructure locale

```bash
docker-compose up -d
```

Services exposés:
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- MinIO API: `localhost:9000`
- MinIO Console: `localhost:9001`
- Worker Celery: service `worker`

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
- docs Swagger: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App:
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

### Infra et stockage
- Docker Compose
- PostgreSQL 15
- Redis 7
- MinIO
- GitNexus pour l'analyse d'impact

## Documentation

Commencer ici:
- [CLAUDE.md](/Users/bilalmeziane/Desktop/Meziane_Monitoring/CLAUDE.md): règles de travail, GitNexus, conventions.
- [docs/README.md](/Users/bilalmeziane/Desktop/Meziane_Monitoring/docs/README.md): index documentaire complet.

Docs principales:
- [PROFIL_ET_OBJECTIFS.md](/Users/bilalmeziane/Desktop/Meziane_Monitoring/docs/architecture/PROFIL_ET_OBJECTIFS.md)
- [ARCHITECTURE_SYSTEME.md](/Users/bilalmeziane/Desktop/Meziane_Monitoring/docs/architecture/ARCHITECTURE_SYSTEME.md)
- [FRONTEND_ARCHITECTURE.md](/Users/bilalmeziane/Desktop/Meziane_Monitoring/docs/architecture/FRONTEND_ARCHITECTURE.md)
- [PLAN.md](/Users/bilalmeziane/Desktop/Meziane_Monitoring/docs/PLAN.md)
- [TRACKING.md](/Users/bilalmeziane/Desktop/Meziane_Monitoring/docs/TRACKING.md)

## Structure

```text
Meziane_Monitoring/
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
npx gitnexus analyze
```

## Sécurité et configuration

- Ne jamais commit de secrets.
- Les variables d'environnement sensibles doivent rester hors du repo.
- Vérifier les valeurs par défaut de `SECRET_KEY`, `DATABASE_URL` et des accès MinIO avant tout déploiement.

## Etat du projet

Le projet dispose déjà:
- d'un backend structuré par domaines
- d'un frontend avec dashboard, agent et admin
- d'une couche documentaire riche
- d'un historique de refactors et RFC dans `docs/refactors/`

L'état détaillé des chantiers en cours et terminés est suivi dans [docs/TRACKING.md](/Users/bilalmeziane/Desktop/Meziane_Monitoring/docs/TRACKING.md).
