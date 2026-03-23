"""
env.py - Configuration Alembic pour migrations

Description:
Configure Alembic pour autogenerate migrations depuis modèles SQLAlchemy.
Import tous les modèles pour détection changes.

Dépendances:
- app.utils.db.Base
- Tous les modèles (sci, bien, transaction, etc.)

Utilisé par:
- alembic CLI
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.utils.db import Base
from app.config import settings

# Import tous les modèles pour autogenerate
from app.models.sci import SCI
from app.models.bien import Bien
from app.models.transaction import Transaction
from app.models.locataire import Locataire
from app.models.bail import Bail
from app.models.quittance import Quittance
from app.models.document import Document
from app.models.document_extraction import DocumentExtraction
from app.models.opportunite import Opportunite
from app.models.simulation import Simulation
from app.models.user import User

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:  # Migrations en mode offline (génération SQL)
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:  # Migrations en mode online (connexion DB)
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
