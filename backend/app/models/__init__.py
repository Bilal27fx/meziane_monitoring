"""
models - Modèles SQLAlchemy (tables DB)

Description:
Package contenant tous les modèles ORM représentant le schéma PostgreSQL.
Chaque fichier = domaine métier (SCI, biens, transactions, etc.).

Dépendances:
- SQLAlchemy 2.0
- utils.db.Base

Utilisé par:
- services/*.py
- api/*.py
- alembic (migrations)
"""
