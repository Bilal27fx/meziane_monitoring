"""Add auction agents foundation

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-03-26 00:10:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


auction_source_status = sa.Enum("ACTIVE", "PAUSED", "DISABLED", name="auctionsourcestatus")
auction_session_status = sa.Enum("DISCOVERED", "FETCHED", "PROCESSED", name="auctionsessionstatus")
auction_listing_status = sa.Enum("DISCOVERED", "NORMALIZED", "ENRICHED", "SHORTLISTED", "REJECTED", name="auctionlistingstatus")
agent_type = sa.Enum("INGESTION", "ENRICHMENT", "ANALYSIS", "RANKING", "ORCHESTRATION", name="agenttype")
agent_status = sa.Enum("ACTIVE", "PAUSED", "DISABLED", name="agentstatus")
agent_run_status = sa.Enum("PENDING", "RUNNING", "SUCCESS", "FAILED", "CANCELLED", name="agentrunstatus")
agent_trigger_type = sa.Enum("MANUAL", "SCHEDULED", "BACKFILL", name="agenttriggertype")

auction_source_status_ref = postgresql.ENUM(name="auctionsourcestatus", create_type=False)
auction_session_status_ref = postgresql.ENUM(name="auctionsessionstatus", create_type=False)
auction_listing_status_ref = postgresql.ENUM(name="auctionlistingstatus", create_type=False)
agent_type_ref = postgresql.ENUM(name="agenttype", create_type=False)
agent_status_ref = postgresql.ENUM(name="agentstatus", create_type=False)
agent_run_status_ref = postgresql.ENUM(name="agentrunstatus", create_type=False)
agent_trigger_type_ref = postgresql.ENUM(name="agenttriggertype", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    auction_source_status.create(bind, checkfirst=True)
    auction_session_status.create(bind, checkfirst=True)
    auction_listing_status.create(bind, checkfirst=True)
    agent_type.create(bind, checkfirst=True)
    agent_status.create(bind, checkfirst=True)
    agent_run_status.create(bind, checkfirst=True)
    agent_trigger_type.create(bind, checkfirst=True)

    op.create_table(
        "auction_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=False),
        sa.Column("status", auction_source_status_ref, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_auction_sources_id"), "auction_sources", ["id"], unique=False)
    op.create_index(op.f("ix_auction_sources_code"), "auction_sources", ["code"], unique=True)

    op.create_table(
        "auction_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=120), nullable=True),
        sa.Column("tribunal", sa.String(length=160), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=False),
        sa.Column("session_datetime", sa.DateTime(), nullable=False),
        sa.Column("announced_listing_count", sa.Integer(), nullable=True),
        sa.Column("status", auction_session_status_ref, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["auction_sources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_url"),
    )
    op.create_index(op.f("ix_auction_sessions_id"), "auction_sessions", ["id"], unique=False)
    op.create_index(op.f("ix_auction_sessions_source_id"), "auction_sessions", ["source_id"], unique=False)
    op.create_index(op.f("ix_auction_sessions_external_id"), "auction_sessions", ["external_id"], unique=False)
    op.create_index(op.f("ix_auction_sessions_tribunal"), "auction_sessions", ["tribunal"], unique=False)
    op.create_index(op.f("ix_auction_sessions_city"), "auction_sessions", ["city"], unique=False)
    op.create_index(op.f("ix_auction_sessions_session_datetime"), "auction_sessions", ["session_datetime"], unique=False)

    op.create_table(
        "agent_definitions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("agent_type", agent_type_ref, nullable=False),
        sa.Column("status", agent_status_ref, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_definitions_id"), "agent_definitions", ["id"], unique=False)
    op.create_index(op.f("ix_agent_definitions_code"), "agent_definitions", ["code"], unique=True)

    op.create_table(
        "agent_parameter_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_definition_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("parameters_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["agent_definition_id"], ["agent_definitions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_parameter_sets_id"), "agent_parameter_sets", ["id"], unique=False)
    op.create_index(op.f("ix_agent_parameter_sets_agent_definition_id"), "agent_parameter_sets", ["agent_definition_id"], unique=False)

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_definition_id", sa.Integer(), nullable=False),
        sa.Column("parameter_set_id", sa.Integer(), nullable=True),
        sa.Column("trigger_type", agent_trigger_type_ref, nullable=False),
        sa.Column("status", agent_run_status_ref, nullable=False),
        sa.Column("parameter_snapshot", sa.JSON(), nullable=False),
        sa.Column("prompt_snapshot", sa.JSON(), nullable=True),
        sa.Column("code_version", sa.String(length=120), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["agent_definition_id"], ["agent_definitions.id"]),
        sa.ForeignKeyConstraint(["parameter_set_id"], ["agent_parameter_sets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_runs_id"), "agent_runs", ["id"], unique=False)
    op.create_index(op.f("ix_agent_runs_agent_definition_id"), "agent_runs", ["agent_definition_id"], unique=False)
    op.create_index(op.f("ix_agent_runs_parameter_set_id"), "agent_runs", ["parameter_set_id"], unique=False)

    op.create_table(
        "auction_listings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=120), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=False),
        sa.Column("reference_annonce", sa.String(length=120), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("listing_type", sa.String(length=80), nullable=True),
        sa.Column("reserve_price", sa.Float(), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("postal_code", sa.String(length=10), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("surface_m2", sa.Float(), nullable=True),
        sa.Column("occupancy_status", sa.String(length=80), nullable=True),
        sa.Column("status", auction_listing_status_ref, nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["auction_sessions.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["auction_sources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_url"),
    )
    op.create_index(op.f("ix_auction_listings_id"), "auction_listings", ["id"], unique=False)
    op.create_index(op.f("ix_auction_listings_source_id"), "auction_listings", ["source_id"], unique=False)
    op.create_index(op.f("ix_auction_listings_session_id"), "auction_listings", ["session_id"], unique=False)
    op.create_index(op.f("ix_auction_listings_external_id"), "auction_listings", ["external_id"], unique=False)
    op.create_index(op.f("ix_auction_listings_city"), "auction_listings", ["city"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_auction_listings_city"), table_name="auction_listings")
    op.drop_index(op.f("ix_auction_listings_external_id"), table_name="auction_listings")
    op.drop_index(op.f("ix_auction_listings_session_id"), table_name="auction_listings")
    op.drop_index(op.f("ix_auction_listings_source_id"), table_name="auction_listings")
    op.drop_index(op.f("ix_auction_listings_id"), table_name="auction_listings")
    op.drop_table("auction_listings")

    op.drop_index(op.f("ix_agent_runs_parameter_set_id"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_agent_definition_id"), table_name="agent_runs")
    op.drop_index(op.f("ix_agent_runs_id"), table_name="agent_runs")
    op.drop_table("agent_runs")

    op.drop_index(op.f("ix_agent_parameter_sets_agent_definition_id"), table_name="agent_parameter_sets")
    op.drop_index(op.f("ix_agent_parameter_sets_id"), table_name="agent_parameter_sets")
    op.drop_table("agent_parameter_sets")

    op.drop_index(op.f("ix_agent_definitions_code"), table_name="agent_definitions")
    op.drop_index(op.f("ix_agent_definitions_id"), table_name="agent_definitions")
    op.drop_table("agent_definitions")

    op.drop_index(op.f("ix_auction_sessions_session_datetime"), table_name="auction_sessions")
    op.drop_index(op.f("ix_auction_sessions_city"), table_name="auction_sessions")
    op.drop_index(op.f("ix_auction_sessions_tribunal"), table_name="auction_sessions")
    op.drop_index(op.f("ix_auction_sessions_external_id"), table_name="auction_sessions")
    op.drop_index(op.f("ix_auction_sessions_source_id"), table_name="auction_sessions")
    op.drop_index(op.f("ix_auction_sessions_id"), table_name="auction_sessions")
    op.drop_table("auction_sessions")

    op.drop_index(op.f("ix_auction_sources_code"), table_name="auction_sources")
    op.drop_index(op.f("ix_auction_sources_id"), table_name="auction_sources")
    op.drop_table("auction_sources")

    bind = op.get_bind()
    agent_trigger_type.drop(bind, checkfirst=True)
    agent_run_status.drop(bind, checkfirst=True)
    agent_status.drop(bind, checkfirst=True)
    agent_type.drop(bind, checkfirst=True)
    auction_listing_status.drop(bind, checkfirst=True)
    auction_session_status.drop(bind, checkfirst=True)
    auction_source_status.drop(bind, checkfirst=True)
