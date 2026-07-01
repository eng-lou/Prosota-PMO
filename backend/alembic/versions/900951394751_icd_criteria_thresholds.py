"""icd criteria thresholds

Revision ID: 900951394751
Revises: ce2b0dd1ef9f
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "900951394751"
down_revision = "ce2b0dd1ef9f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "icd_criteria",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("dimension", sa.String(length=30), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "dimension", "level", name="uq_icd_criteria_project_dimension_level"),
    )


def downgrade() -> None:
    op.drop_table("icd_criteria")
