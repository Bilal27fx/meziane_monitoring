"""add auction listing scoring columns

Revision ID: a1b2c3d4e5f6
Revises: f6a7b8c9d0e1
Create Date: 2026-04-03

"""
from alembic import op
import sqlalchemy as sa

revision = 'b3c4d5e6f7a8'
down_revision = '0f1e2d3c4b5a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('auction_listings', sa.Column('score_global', sa.Integer(), nullable=True))
    op.add_column('auction_listings', sa.Column('score_localisation', sa.Integer(), nullable=True))
    op.add_column('auction_listings', sa.Column('score_prix', sa.Integer(), nullable=True))
    op.add_column('auction_listings', sa.Column('score_potentiel', sa.Integer(), nullable=True))
    op.add_column('auction_listings', sa.Column('loyer_estime', sa.Float(), nullable=True))
    op.add_column('auction_listings', sa.Column('rentabilite_brute', sa.Float(), nullable=True))
    op.add_column('auction_listings', sa.Column('raison_score', sa.Text(), nullable=True))
    op.add_column('auction_listings', sa.Column('risques_llm', sa.JSON(), nullable=True))
    op.add_column('auction_listings', sa.Column('recommandation', sa.String(30), nullable=True))
    op.add_column('auction_listings', sa.Column('scored_at', sa.DateTime(), nullable=True))
    op.create_index('ix_auction_listings_score_global', 'auction_listings', ['score_global'])


def downgrade() -> None:
    op.drop_index('ix_auction_listings_score_global', table_name='auction_listings')
    op.drop_column('auction_listings', 'scored_at')
    op.drop_column('auction_listings', 'recommandation')
    op.drop_column('auction_listings', 'risques_llm')
    op.drop_column('auction_listings', 'raison_score')
    op.drop_column('auction_listings', 'rentabilite_brute')
    op.drop_column('auction_listings', 'loyer_estime')
    op.drop_column('auction_listings', 'score_potentiel')
    op.drop_column('auction_listings', 'score_prix')
    op.drop_column('auction_listings', 'score_localisation')
    op.drop_column('auction_listings', 'score_global')
