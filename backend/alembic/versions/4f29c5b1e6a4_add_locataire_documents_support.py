"""Add locataire documents support

Revision ID: 4f29c5b1e6a4
Revises: 030422323a95
Create Date: 2026-03-17 00:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4f29c5b1e6a4"
down_revision: Union[str, None] = "030422323a95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL enum values are stored by member name (uppercase)
    op.execute("ALTER TYPE typedocument ADD VALUE IF NOT EXISTS 'PIECE_IDENTITE'")
    op.execute("ALTER TYPE typedocument ADD VALUE IF NOT EXISTS 'JUSTIFICATIF_DOMICILE'")
    op.execute("ALTER TYPE typedocument ADD VALUE IF NOT EXISTS 'CONTRAT_TRAVAIL'")
    op.execute("ALTER TYPE typedocument ADD VALUE IF NOT EXISTS 'FICHE_PAIE'")
    op.execute("ALTER TYPE typedocument ADD VALUE IF NOT EXISTS 'AVIS_IMPOSITION'")
    op.execute("ALTER TYPE typedocument ADD VALUE IF NOT EXISTS 'RIB'")
    op.execute("ALTER TYPE typedocument ADD VALUE IF NOT EXISTS 'ASSURANCE_HABITATION'")
    op.execute("ALTER TYPE typedocument ADD VALUE IF NOT EXISTS 'ACTE_CAUTION_SOLIDAIRE'")
    op.execute("ALTER TYPE typedocument ADD VALUE IF NOT EXISTS 'QUITTANCE_LOYER_PRECEDENTE'")

    op.add_column("documents", sa.Column("locataire_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_documents_locataire_id"), "documents", ["locataire_id"], unique=False)
    op.create_foreign_key(
        "fk_documents_locataire_id_locataires",
        "documents",
        "locataires",
        ["locataire_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_documents_locataire_id_locataires", "documents", type_="foreignkey")
    op.drop_index(op.f("ix_documents_locataire_id"), table_name="documents")
    op.drop_column("documents", "locataire_id")

    # PostgreSQL does not support removing enum values without full type recreation.
