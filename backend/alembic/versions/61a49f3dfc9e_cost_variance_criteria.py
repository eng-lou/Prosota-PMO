"""cost variance criteria (configurable thresholds)

Revision ID: 61a49f3dfc9e
Revises: a4404274658f
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "61a49f3dfc9e"
down_revision = "a4404274658f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cost_variance_criteria",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=50), nullable=False),
        sa.Column("min_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("max_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "level", name="uq_cost_variance_criteria_project_level"),
    )


def downgrade() -> None:
    op.drop_table("cost_variance_criteria")
