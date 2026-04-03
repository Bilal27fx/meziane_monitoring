# Backend Meziane Monitoring

API FastAPI du projet Meziane Monitoring.

## Rôle

Le backend centralise:
- les routes API métier
- les modèles et schémas
- les services métier
- les tâches asynchrones
- les intégrations externes

## Démarrage

### 1. Installer les dépendances

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Lancer l'infrastructure locale

```bash
cd ..
docker-compose up -d
cd backend
```

### 3. Appliquer les migrations

```bash
alembic upgrade head
```

### 4. Lancer l'API

```bash
uvicorn app.main:app --reload
```

API:
- base: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Commandes utiles

```bash
# Nouvelle migration
alembic revision --autogenerate -m "description"

# Appliquer migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Tests
pytest

# Qualité
black app tests
ruff check app tests
```

## Structure

```text
backend/
├── app/
│   ├── api/            # Routes FastAPI
│   ├── agents/         # Agents et logique IA
│   ├── connectors/     # APIs externes
│   ├── models/         # Modèles SQLAlchemy
│   ├── plugins/        # Extensions backend
│   ├── schemas/        # Schémas Pydantic
│   ├── services/       # Logique métier
│   ├── tasks/          # Tâches Celery
│   └── utils/          # Outils transverses
├── alembic/            # Migrations DB
├── tests/              # Tests backend
└── requirements.txt
```

## Documentation liée

- `../README.md`: vue d'ensemble du repo
- `../CLAUDE.md`: règles de travail et GitNexus
- `../docs/architecture/ARCHITECTURE_SYSTEME.md`: architecture backend cible
