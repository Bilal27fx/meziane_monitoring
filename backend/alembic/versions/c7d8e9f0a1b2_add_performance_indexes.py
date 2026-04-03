"""Add performance indexes for scalability

Revision ID: c7d8e9f0a1b2
Revises: b2c3d4e5f6a7
Create Date: 2026-03-24 00:00:00.000000

RFC-007 — Audit scalabilité : aucun index n'existait sur les colonnes
filtrées dans le dashboard. Full table scan sur chaque requête.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "c7d8e9f0a1b2"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Composite index transactions — non couvert par les index initiaux
    op.create_index("ix_transaction_sci_id_date", "transactions", ["sci_id", "date"])

    # Baux — statut non indexé dans la migration initiale
    op.create_index("ix_bail_statut", "baux", ["statut"])

    # Quittances — statut + composite non couverts
    op.create_index("ix_quittance_statut", "quittances", ["statut"])
    op.create_index("ix_quittance_bail_id_statut", "quittances", ["bail_id", "statut"])

    # Opportunités — statut non indexé dans la migration initiale
    op.create_index("ix_opportunite_statut", "opportunites_immobilieres", ["statut"])

    # Biens — statut non indexé dans la migration initiale
    op.create_index("ix_bien_statut", "biens", ["statut"])


def downgrade() -> None:
    op.drop_index("ix_bien_statut", table_name="biens")
    op.drop_index("ix_opportunite_statut", table_name="opportunites_immobilieres")
    op.drop_index("ix_quittance_bail_id_statut", table_name="quittances")
    op.drop_index("ix_quittance_statut", table_name="quittances")
    op.drop_index("ix_bail_statut", table_name="baux")
    op.drop_index("ix_transaction_sci_id_date", table_name="transactions")
