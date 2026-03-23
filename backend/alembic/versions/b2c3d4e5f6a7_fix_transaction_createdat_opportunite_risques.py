"""Fix Transaction.created_at to DateTime, Opportunite.risques to JSON

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-23 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Transaction.created_at Date → DateTime
    op.alter_column(
        "transactions",
        "created_at",
        existing_type=sa.Date(),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="created_at::timestamp",
    )

    # Opportunite.risques Text → JSON
    op.alter_column(
        "opportunites_immobilieres",
        "risques",
        existing_type=sa.Text(),
        type_=sa.JSON(),
        existing_nullable=True,
        postgresql_using="risques::json",
    )


def downgrade() -> None:
    op.alter_column(
        "opportunites_immobilieres",
        "risques",
        existing_type=sa.JSON(),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "transactions",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.Date(),
        existing_nullable=False,
    )
