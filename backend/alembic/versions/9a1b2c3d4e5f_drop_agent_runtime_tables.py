"""Drop legacy agent runtime tables

Revision ID: 9a1b2c3d4e5f
Revises: f7a8b9c0d1e2
Create Date: 2026-04-04 22:15:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9a1b2c3d4e5f"
down_revision: Union[str, None] = "f7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


AGENT_TABLES = [
    "agent_run_events",
    "auction_listings",
    "agent_runs",
    "agent_parameter_sets",
    "agent_definitions",
    "auction_sessions",
    "auction_sources",
    "opportunites_immobilieres",
]

AGENT_ENUM_TYPES = [
    "agentruneventlevel",
    "auctionlistingstatus",
    "agentrunstatus",
    "agenttriggertype",
    "agentstatus",
    "agenttype",
    "auctionsessionstatus",
    "auctionsourcestatus",
    "sourceannonce",
    "statutopportunite",
]


def _drop_simulation_opportunity_link() -> None:
    op.execute(
        sa.text(
            'ALTER TABLE simulations_acquisition '
            'DROP CONSTRAINT IF EXISTS simulations_acquisition_opportunite_id_fkey'
        )
    )
    op.drop_column("simulations_acquisition", "opportunite_id")


def _drop_enum_types() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    for type_name in AGENT_ENUM_TYPES:
        op.execute(sa.text(f'DROP TYPE IF EXISTS "{type_name}"'))


def upgrade() -> None:
    _drop_simulation_opportunity_link()

    for table_name in AGENT_TABLES:
        op.drop_table(table_name)

    _drop_enum_types()


def downgrade() -> None:
    raise NotImplementedError(
        "Downgrade non pris en charge: la suppression des tables agent est volontairement irreversible."
    )
