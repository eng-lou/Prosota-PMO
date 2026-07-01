"""risk module phase 5: configurable probability/impact criteria & thresholds

Project-level, editable definitions of what each probability/impact level
means (e.g. "Medium probability = 25-50%"), matching the prototype's Criteria
& Thresholds tab. Per PMBOK7/Rita Mulcahy: standardising these definitions is
part of the risk management plan, so different people rating a risk "High"
mean the same thing. Two dedicated tables since probability and impact
criteria have different shapes (impact needs both a cost AND a schedule
range per level). See docs/RISK_MODULE_PLAN.md Phase 5.

Revision ID: b9d4f28c6e51
Revises: a2b8e1c76d40
Create Date: 2026-07-01 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b9d4f28c6e51'
down_revision: Union[str, None] = 'a2b8e1c76d40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'risk_probability_criteria',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=50), nullable=False),
        sa.Column('min_probability', sa.Numeric(5, 2), nullable=False),
        sa.Column('max_probability', sa.Numeric(5, 2), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('project_id', 'level', name='uq_risk_probability_criteria_project_level'),
    )

    op.create_table(
        'risk_impact_criteria',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=50), nullable=False),
        sa.Column('min_cost', sa.Numeric(14, 2), nullable=True),
        sa.Column('max_cost', sa.Numeric(14, 2), nullable=True),
        sa.Column('min_schedule_days', sa.Integer(), nullable=True),
        sa.Column('max_schedule_days', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('project_id', 'level', name='uq_risk_impact_criteria_project_level'),
    )


def downgrade() -> None:
    op.drop_table('risk_impact_criteria')
    op.drop_table('risk_probability_criteria')
