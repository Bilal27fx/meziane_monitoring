"""add auction listing property metadata

Revision ID: d9e8f7a6b5c4
Revises: c4d5e6f7a8b9
Create Date: 2026-04-03 22:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d9e8f7a6b5c4"
down_revision = "c4d5e6f7a8b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("auction_listings", sa.Column("nb_pieces", sa.Integer(), nullable=True))
    op.add_column("auction_listings", sa.Column("nb_chambres", sa.Integer(), nullable=True))
    op.add_column("auction_listings", sa.Column("etage", sa.Integer(), nullable=True))
    op.add_column("auction_listings", sa.Column("type_etage", sa.String(length=80), nullable=True))
    op.add_column("auction_listings", sa.Column("ascenseur", sa.Boolean(), nullable=True))
    op.add_column("auction_listings", sa.Column("balcon", sa.Boolean(), nullable=True))
    op.add_column("auction_listings", sa.Column("terrasse", sa.Boolean(), nullable=True))
    op.add_column("auction_listings", sa.Column("cave", sa.Boolean(), nullable=True))
    op.add_column("auction_listings", sa.Column("parking", sa.Boolean(), nullable=True))
    op.add_column("auction_listings", sa.Column("box", sa.Boolean(), nullable=True))
    op.add_column("auction_listings", sa.Column("jardin", sa.Boolean(), nullable=True))
    op.add_column("auction_listings", sa.Column("property_details", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("auction_listings", "property_details")
    op.drop_column("auction_listings", "jardin")
    op.drop_column("auction_listings", "box")
    op.drop_column("auction_listings", "parking")
    op.drop_column("auction_listings", "cave")
    op.drop_column("auction_listings", "terrasse")
    op.drop_column("auction_listings", "balcon")
    op.drop_column("auction_listings", "ascenseur")
    op.drop_column("auction_listings", "type_etage")
    op.drop_column("auction_listings", "etage")
    op.drop_column("auction_listings", "nb_chambres")
    op.drop_column("auction_listings", "nb_pieces")
