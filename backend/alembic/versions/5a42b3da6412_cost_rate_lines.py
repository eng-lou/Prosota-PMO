"""cost rate lines (Qty x Unit x Rate build-up sub-list)

Revision ID: 5a42b3da6412
Revises: 61a49f3dfc9e
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "5a42b3da6412"
down_revision = "61a49f3dfc9e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cost_rate_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cost_element_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cost_elements.id"), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("qty", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("rate", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("cost_rate_lines")
