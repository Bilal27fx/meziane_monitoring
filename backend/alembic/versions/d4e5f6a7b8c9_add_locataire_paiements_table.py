"""Add locataire paiements table

Revision ID: d4e5f6a7b8c9
Revises: c7d8e9f0a1b2
Create Date: 2026-03-25 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c7d8e9f0a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


mode_paiement_enum = sa.Enum(
    "VIREMENT",
    "PRELEVEMENT",
    "CARTE",
    "CHEQUE",
    "ESPECES",
    "AUTRE",
    name="modepaiement",
)

mode_paiement_enum_existing = postgresql.ENUM(
    "VIREMENT",
    "PRELEVEMENT",
    "CARTE",
    "CHEQUE",
    "ESPECES",
    "AUTRE",
    name="modepaiement",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    mode_paiement_enum.create(bind, checkfirst=True)

    op.create_table(
        "locataire_paiements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("locataire_id", sa.Integer(), nullable=False),
        sa.Column("bail_id", sa.Integer(), nullable=False),
        sa.Column("quittance_id", sa.Integer(), nullable=True),
        sa.Column("date_paiement", sa.Date(), nullable=False),
        sa.Column("montant", sa.Float(), nullable=False),
        sa.Column("mode_paiement", mode_paiement_enum_existing, nullable=False, server_default="VIREMENT"),
        sa.Column("reference", sa.String(length=120), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["bail_id"], ["baux.id"]),
        sa.ForeignKeyConstraint(["locataire_id"], ["locataires.id"]),
        sa.ForeignKeyConstraint(["quittance_id"], ["quittances.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_locataire_paiements_id"), "locataire_paiements", ["id"], unique=False)
    op.create_index(op.f("ix_locataire_paiements_locataire_id"), "locataire_paiements", ["locataire_id"], unique=False)
    op.create_index(op.f("ix_locataire_paiements_bail_id"), "locataire_paiements", ["bail_id"], unique=False)
    op.create_index(op.f("ix_locataire_paiements_quittance_id"), "locataire_paiements", ["quittance_id"], unique=False)
    op.create_index(op.f("ix_locataire_paiements_date_paiement"), "locataire_paiements", ["date_paiement"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_locataire_paiements_date_paiement"), table_name="locataire_paiements")
    op.drop_index(op.f("ix_locataire_paiements_quittance_id"), table_name="locataire_paiements")
    op.drop_index(op.f("ix_locataire_paiements_bail_id"), table_name="locataire_paiements")
    op.drop_index(op.f("ix_locataire_paiements_locataire_id"), table_name="locataire_paiements")
    op.drop_index(op.f("ix_locataire_paiements_id"), table_name="locataire_paiements")
    op.drop_table("locataire_paiements")

    bind = op.get_bind()
    mode_paiement_enum.drop(bind, checkfirst=True)
