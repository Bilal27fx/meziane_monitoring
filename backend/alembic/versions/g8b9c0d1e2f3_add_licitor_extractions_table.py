"""add_licitor_extractions_table

Revision ID: g8b9c0d1e2f3
Revises: f7a8b9c0d1e2
Create Date: 2026-04-04 00:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = "g8b9c0d1e2f3"
down_revision = "f7a8b9c0d1e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "licitor_extractions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), sa.ForeignKey("auction_listings.id"), nullable=False),
        sa.Column("raw_sections", sa.JSON(), nullable=True),
        sa.Column("llm_raw_response", sa.Text(), nullable=True),
        sa.Column("parsed_extraction", sa.JSON(), nullable=True),
        sa.Column("extraction_model", sa.String(60), nullable=True),
        sa.Column("extracted_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("listing_id"),
    )
    op.create_index("ix_licitor_extractions_listing_id", "licitor_extractions", ["listing_id"])


def downgrade() -> None:
    op.drop_index("ix_licitor_extractions_listing_id", table_name="licitor_extractions")
    op.drop_table("licitor_extractions")
