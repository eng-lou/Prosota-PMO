"""icd last_reviewed_date and reassessment log

Revision ID: d601e4a2b7a6
Revises: 900951394751
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "d601e4a2b7a6"
down_revision = "900951394751"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('icd_items', sa.Column('last_reviewed_date', sa.Date(), nullable=True))

    op.create_table(
        "icd_reassessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("icd_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("icd_items.id"), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("icd_reassessments")
    op.drop_column('icd_items', 'last_reviewed_date')
