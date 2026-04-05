"""add_auction_notification_tracking_fields

Revision ID: h1i2j3k4l5m6
Revises: g8b9c0d1e2f3
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa

revision = "h1i2j3k4l5m6"
down_revision = "g8b9c0d1e2f3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("auction_listings", sa.Column("telegram_notified_at", sa.DateTime(), nullable=True))
    op.add_column("auction_listings", sa.Column("telegram_notified_for_visit_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("auction_listings", "telegram_notified_for_visit_at")
    op.drop_column("auction_listings", "telegram_notified_at")
