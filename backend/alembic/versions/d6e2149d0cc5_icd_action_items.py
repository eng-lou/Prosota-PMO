"""icd action items sub-list

Revision ID: d6e2149d0cc5
Revises: 63df6368364e
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "d6e2149d0cc5"
down_revision = "63df6368364e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "icd_action_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("icd_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("icd_items.id"), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="not_started"),
        sa.Column("pct_complete", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("icd_action_items")
