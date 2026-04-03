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


def load_all_models() -> None:
    """Charge tous les modules ORM pour enregistrer les mappers SQLAlchemy."""
    from app.models import agent_definition, agent_parameter_set, agent_run, agent_run_event  # noqa: F401
    from app.models import auction_listing, auction_session, auction_source  # noqa: F401
    from app.models import bail, bien, document, document_extraction, document_folder  # noqa: F401
    from app.models import locataire, locataire_paiement, opportunite, quittance  # noqa: F401
    from app.models import sci, simulation, transaction, user  # noqa: F401
