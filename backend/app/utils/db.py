"""
db.py - Gestion connexion base de données

Description:
Configuration SQLAlchemy engine et session factory.
Fournit Base déclarative pour modèles ORM.
Dependency injection pour FastAPI.

Dépendances:
- SQLAlchemy 2.0
- config.settings

Utilisé par:
- models/*.py (héritage Base)
- api/*.py (dependency get_db)
- services/*.py (sessions DB)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)  # Engine SQLAlchemy avec echo en dev

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Factory sessions DB

Base = declarative_base()  # Classe de base pour modèles ORM


def get_db() -> Session:  # Dépendance FastAPI fournissant session DB avec auto-cleanup
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
