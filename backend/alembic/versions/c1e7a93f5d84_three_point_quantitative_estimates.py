"""risk module phase 6: 3-point (min/most likely/max) quantitative estimates

Renames cost_impact -> cost_most_likely and schedule_impact_days ->
schedule_most_likely_days (safe — nothing using the old names is committed
yet), and adds cost_min/cost_max/schedule_min_days/schedule_max_days.
Matches the prototype's Quantitative Analysis tab (3-point estimate +
distribution chart). EMV continues to use the most-likely value — the
reference material's own worked EMV examples are all single-point, so a
PERT-weighted formula would not be something we could verify against source.
See docs/RISK_MODULE_PLAN.md Phase 6.

Revision ID: c1e7a93f5d84
Revises: b9d4f28c6e51
Create Date: 2026-07-01 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1e7a93f5d84'
down_revision: Union[str, None] = 'b9d4f28c6e51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('risks', 'cost_impact', new_column_name='cost_most_likely')
    op.alter_column('risks', 'schedule_impact_days', new_column_name='schedule_most_likely_days')
    op.add_column('risks', sa.Column('cost_min', sa.Numeric(14, 2), nullable=True))
    op.add_column('risks', sa.Column('cost_max', sa.Numeric(14, 2), nullable=True))
    op.add_column('risks', sa.Column('schedule_min_days', sa.Integer(), nullable=True))
    op.add_column('risks', sa.Column('schedule_max_days', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('risks', 'schedule_max_days')
    op.drop_column('risks', 'schedule_min_days')
    op.drop_column('risks', 'cost_max')
    op.drop_column('risks', 'cost_min')
    op.alter_column('risks', 'schedule_most_likely_days', new_column_name='schedule_impact_days')
    op.alter_column('risks', 'cost_most_likely', new_column_name='cost_impact')
