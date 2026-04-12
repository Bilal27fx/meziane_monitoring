"""add_langgraph_columns_to_agent_runs

Révision ID: i2j3k4l5m6n7
Revises: h1i2j3k4l5m6
Create Date: 2026-04-12

Ajoute les colonnes nécessaires au pipeline LangGraph :
- source_code : identifiant de la source ("licitor")
- result_summary : résumé JSON du run (listings, scores, tokens)
- thread_id : thread_id LangGraph pour checkpointing
- error : message d'erreur si run échoué

Rend agent_definition_id et trigger_type nullables (remplacés par source_code).
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "i2j3k4l5m6n7"
down_revision = "h1i2j3k4l5m6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Nouvelles colonnes LangGraph
    op.add_column("agent_runs", sa.Column("source_code", sa.String(length=80), nullable=True))
    op.add_column("agent_runs", sa.Column("result_summary", postgresql.JSONB(), nullable=True, server_default="{}"))
    op.add_column("agent_runs", sa.Column("thread_id", sa.String(length=255), nullable=True))
    op.add_column("agent_runs", sa.Column("error", sa.Text(), nullable=True))

    # Rendre les anciennes colonnes nullables (plus utilisées par le nouveau pipeline)
    op.alter_column("agent_runs", "agent_definition_id", nullable=True)
    op.alter_column("agent_runs", "trigger_type", nullable=True)
    op.alter_column("agent_runs", "started_at", nullable=True)

    # Index sur thread_id pour le checkpointing LangGraph
    op.create_index("ix_agent_runs_thread_id", "agent_runs", ["thread_id"], unique=True)
    op.create_index("ix_agent_runs_source_code", "agent_runs", ["source_code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_agent_runs_source_code", table_name="agent_runs")
    op.drop_index("ix_agent_runs_thread_id", table_name="agent_runs")
    op.drop_column("agent_runs", "error")
    op.drop_column("agent_runs", "thread_id")
    op.drop_column("agent_runs", "result_summary")
    op.drop_column("agent_runs", "source_code")
