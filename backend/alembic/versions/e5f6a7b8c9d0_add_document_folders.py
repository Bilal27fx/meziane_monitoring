"""Add document folders

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-03-25 16:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document_folders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sci_id", sa.Integer(), nullable=False),
        sa.Column("bien_id", sa.Integer(), nullable=True),
        sa.Column("locataire_id", sa.Integer(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("nom", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["bien_id"], ["biens.id"]),
        sa.ForeignKeyConstraint(["locataire_id"], ["locataires.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["document_folders.id"]),
        sa.ForeignKeyConstraint(["sci_id"], ["sci.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_folders_id"), "document_folders", ["id"], unique=False)
    op.create_index(op.f("ix_document_folders_sci_id"), "document_folders", ["sci_id"], unique=False)
    op.create_index(op.f("ix_document_folders_bien_id"), "document_folders", ["bien_id"], unique=False)
    op.create_index(op.f("ix_document_folders_locataire_id"), "document_folders", ["locataire_id"], unique=False)
    op.create_index(op.f("ix_document_folders_parent_id"), "document_folders", ["parent_id"], unique=False)

    op.add_column("documents", sa.Column("folder_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_documents_folder_id"), "documents", ["folder_id"], unique=False)
    op.create_foreign_key(
        "fk_documents_folder_id_document_folders",
        "documents",
        "document_folders",
        ["folder_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_documents_folder_id_document_folders", "documents", type_="foreignkey")
    op.drop_index(op.f("ix_documents_folder_id"), table_name="documents")
    op.drop_column("documents", "folder_id")

    op.drop_index(op.f("ix_document_folders_parent_id"), table_name="document_folders")
    op.drop_index(op.f("ix_document_folders_locataire_id"), table_name="document_folders")
    op.drop_index(op.f("ix_document_folders_bien_id"), table_name="document_folders")
    op.drop_index(op.f("ix_document_folders_sci_id"), table_name="document_folders")
    op.drop_index(op.f("ix_document_folders_id"), table_name="document_folders")
    op.drop_table("document_folders")
