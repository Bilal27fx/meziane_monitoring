"""add hybrid auction scoring fields

Revision ID: e1f2a3b4c5d6
Revises: d9e8f7a6b5c4
Create Date: 2026-04-03 22:40:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "e1f2a3b4c5d6"
down_revision = "d9e8f7a6b5c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("auction_listings", sa.Column("score_cible_paris_petite_surface", sa.Integer(), nullable=True))
    op.add_column("auction_listings", sa.Column("score_liquidite", sa.Integer(), nullable=True))
    op.add_column("auction_listings", sa.Column("score_occupation", sa.Integer(), nullable=True))
    op.add_column("auction_listings", sa.Column("score_qualite_bien", sa.Integer(), nullable=True))
    op.add_column("auction_listings", sa.Column("bonus_strategique", sa.Integer(), nullable=True))
    op.add_column("auction_listings", sa.Column("categorie_investissement", sa.String(length=40), nullable=True))
    op.add_column("auction_listings", sa.Column("travaux_estimes", sa.Float(), nullable=True))
    op.add_column("auction_listings", sa.Column("valeur_marche_estimee", sa.Float(), nullable=True))
    op.add_column("auction_listings", sa.Column("valeur_marche_ajustee", sa.Float(), nullable=True))
    op.add_column("auction_listings", sa.Column("prix_max_cible", sa.Float(), nullable=True))
    op.add_column("auction_listings", sa.Column("prix_max_agressif", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("auction_listings", "prix_max_agressif")
    op.drop_column("auction_listings", "prix_max_cible")
    op.drop_column("auction_listings", "valeur_marche_ajustee")
    op.drop_column("auction_listings", "valeur_marche_estimee")
    op.drop_column("auction_listings", "travaux_estimes")
    op.drop_column("auction_listings", "categorie_investissement")
    op.drop_column("auction_listings", "bonus_strategique")
    op.drop_column("auction_listings", "score_qualite_bien")
    op.drop_column("auction_listings", "score_occupation")
    op.drop_column("auction_listings", "score_liquidite")
    op.drop_column("auction_listings", "score_cible_paris_petite_surface")
