"""add_telegram_notified_to_auction_listing

Revision ID: f7a8b9c0d1e2
Revises: e1f2a3b4c5d6
Create Date: 2026-04-04

"""
from alembic import op
import sqlalchemy as sa

revision = "f7a8b9c0d1e2"
down_revision = "e1f2a3b4c5d6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "auction_listings",
        sa.Column("telegram_notified", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade():
    op.drop_column("auction_listings", "telegram_notified")
