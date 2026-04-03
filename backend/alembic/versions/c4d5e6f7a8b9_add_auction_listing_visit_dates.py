"""add auction listing visit_dates

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-04-03

"""
from alembic import op
import sqlalchemy as sa

revision = 'c4d5e6f7a8b9'
down_revision = 'b3c4d5e6f7a8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('auction_listings', sa.Column('visit_dates', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('auction_listings', 'visit_dates')
