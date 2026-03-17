# Backend Meziane Monitoring

API FastAPI pour système de monitoring patrimoine immobilier.

## Setup

### 1. Copier .env
```bash
cp ../.env.example ../.env
# Éditer .env avec tes vraies valeurs
```

### 2. Installer dépendances
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. Lancer infrastructure Docker
```bash
cd ..
docker-compose up -d
```

### 4. Créer migration initiale
```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 5. Lancer serveur
```bash
uvicorn app.main:app --reload
```

API disponible : http://localhost:8000
Docs : http://localhost:8000/docs

## Commandes Utiles

```bash
# Créer migration
alembic revision --autogenerate -m "Description"

# Appliquer migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Tests
pytest

# Format code
black app/
ruff check app/
```

## Structure

```
backend/
├── app/
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   ├── api/            # FastAPI routes
│   ├── connectors/     # External APIs
│   ├── agents/         # AI agents
│   ├── tasks/          # Celery tasks
│   └── utils/          # Utilities
├── alembic/            # DB migrations
└── tests/              # Tests
```
