"""add_langgraph_columns_to_agent_runs

Revision ID: i2j3k4l5m6n7
Revises: h1i2j3k4l5m6
Create Date: 2026-04-12

Ajoute les colonnes necessaires au pipeline LangGraph :
- source_code, result_summary, thread_id, error
Rend agent_definition_id et trigger_type nullables.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "i2j3k4l5m6n7"
down_revision = "h1i2j3k4l5m6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Colonnes deja appliquees a la DB — migration reconstituee pour aligner la chaine Alembic
    bind = op.get_bind()

    # Ajouter source_code si absent
    inspector = sa.inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("agent_runs")]

    if "source_code" not in columns:
        op.add_column("agent_runs", sa.Column("source_code", sa.String(length=80), nullable=True))
    if "result_summary" not in columns:
        op.add_column("agent_runs", sa.Column("result_summary", postgresql.JSONB(), nullable=True, server_default="{}"))
    if "thread_id" not in columns:
        op.add_column("agent_runs", sa.Column("thread_id", sa.String(length=255), nullable=True))
    if "error" not in columns:
        op.add_column("agent_runs", sa.Column("error", sa.Text(), nullable=True))

    op.alter_column("agent_runs", "agent_definition_id", nullable=True)
    op.alter_column("agent_runs", "trigger_type", nullable=True)
    op.alter_column("agent_runs", "started_at", nullable=True)

    # Index (idempotent)
    indexes = [i["name"] for i in inspector.get_indexes("agent_runs")]
    if "ix_agent_runs_thread_id" not in indexes:
        op.create_index("ix_agent_runs_thread_id", "agent_runs", ["thread_id"], unique=True)
    if "ix_agent_runs_source_code" not in indexes:
        op.create_index("ix_agent_runs_source_code", "agent_runs", ["source_code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_agent_runs_source_code", table_name="agent_runs")
    op.drop_index("ix_agent_runs_thread_id", table_name="agent_runs")
    op.drop_column("agent_runs", "error")
    op.drop_column("agent_runs", "thread_id")
    op.drop_column("agent_runs", "result_summary")
    op.drop_column("agent_runs", "source_code")
