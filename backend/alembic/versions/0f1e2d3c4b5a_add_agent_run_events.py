"""Add agent run events

Revision ID: 0f1e2d3c4b5a
Revises: f6a7b8c9d0e1
Create Date: 2026-03-26 00:35:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0f1e2d3c4b5a"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


agent_run_event_level = sa.Enum("DEBUG", "INFO", "WARNING", "ERROR", name="agentruneventlevel")
agent_run_event_level_ref = postgresql.ENUM(name="agentruneventlevel", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    agent_run_event_level.create(bind, checkfirst=True)

    op.create_table(
        "agent_run_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("level", agent_run_event_level_ref, nullable=False),
        sa.Column("step", sa.String(length=80), nullable=True),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_run_events_id"), "agent_run_events", ["id"], unique=False)
    op.create_index(op.f("ix_agent_run_events_run_id"), "agent_run_events", ["run_id"], unique=False)
    op.create_index(op.f("ix_agent_run_events_step"), "agent_run_events", ["step"], unique=False)
    op.create_index(op.f("ix_agent_run_events_event_type"), "agent_run_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_agent_run_events_created_at"), "agent_run_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_run_events_created_at"), table_name="agent_run_events")
    op.drop_index(op.f("ix_agent_run_events_event_type"), table_name="agent_run_events")
    op.drop_index(op.f("ix_agent_run_events_step"), table_name="agent_run_events")
    op.drop_index(op.f("ix_agent_run_events_run_id"), table_name="agent_run_events")
    op.drop_index(op.f("ix_agent_run_events_id"), table_name="agent_run_events")
    op.drop_table("agent_run_events")

    bind = op.get_bind()
    agent_run_event_level.drop(bind, checkfirst=True)
