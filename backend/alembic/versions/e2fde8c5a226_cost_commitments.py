"""cost commitments (open PO sub-list)

Revision ID: e2fde8c5a226
Revises: 5a42b3da6412
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "e2fde8c5a226"
down_revision = "5a42b3da6412"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cost_commitments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cost_element_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cost_elements.id"), nullable=False),
        sa.Column("po_reference", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("cost_commitments")
