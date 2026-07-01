"""icd comments

Revision ID: b1094c80580b
Revises: d6e2149d0cc5
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "b1094c80580b"
down_revision = "d6e2149d0cc5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "icd_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("icd_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("icd_items.id"), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("author_name", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("icd_comments")
