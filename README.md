# Meziane Monitoring System

Système de monitoring et gestion patrimoine immobilier avec agents IA.

## 📋 Documentation

- **[PROFIL_ET_OBJECTIFS.md](./PROFIL_ET_OBJECTIFS.md)** - Profil Bilal, objectifs business
- **[ARCHITECTURE_SYSTEME.md](./ARCHITECTURE_SYSTEME.md)** - Architecture complète du système
- **[CLAUDE_INSTRUCTIONS.md](./CLAUDE_INSTRUCTIONS.md)** - Règles développement

## 🚀 Quick Start

### 1. Configuration
```bash
cp .env.example .env
# Éditer .env avec tes credentials
```

### 2. Lancer infrastructure
```bash
docker-compose up -d
```

Services disponibles :
- PostgreSQL : `localhost:5432`
- Redis : `localhost:6379`
- MinIO : `localhost:9000` (UI: `localhost:9001`)

### 3. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Migrations DB
alembic upgrade head

# Lancer API
uvicorn app.main:app --reload
```

API : http://localhost:8000

### 4. Setup Frontend (à venir)
```bash
cd frontend
npm install
npm run dev
```

## 🏗️ Stack Technique

**Backend**
- Python 3.11+
- FastAPI
- SQLAlchemy + PostgreSQL
- Redis
- LangGraph + Claude

**Storage**
- PostgreSQL 15
- MinIO (S3-compatible)
- Redis 7

**Frontend** (à venir)
- Next.js 14
- React
- TypeScript
- Tailwind CSS

## 📁 Structure Projet

```
meziane_monitoring/
├── backend/            # API FastAPI + services
├── frontend/           # Dashboard Next.js (à venir)
├── docs/               # Documentation
├── docker-compose.yml  # Infrastructure
└── .env.example        # Variables d'environnement
```

## 🎯 Phase Actuelle

**Phase 1 : Infrastructure & Base** ✅
- Docker Compose
- Modèles SQLAlchemy
- Migrations Alembic
- Structure backend

**Phase 2 : Ingestion Données** (en cours)
- Banking Connector
- Transaction Parser
- Categorizer IA

## 📝 Commandes Utiles

```bash
# Infrastructure
docker-compose up -d
docker-compose logs -f
docker-compose down

# Backend
cd backend
uvicorn app.main:app --reload
alembic revision --autogenerate -m "Description"
alembic upgrade head
pytest

# Format
black backend/app
ruff check backend/app
```

## 🔐 Sécurité

- Ne jamais commit `.env`
- API keys dans variables d'environnement
- `.env.example` fourni sans vraies valeurs

## 👤 Développeur

Bilal Meziane - Objectif : 20 appartements d'ici 2030
