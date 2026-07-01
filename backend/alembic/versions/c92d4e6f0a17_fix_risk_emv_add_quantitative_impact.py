"""fix risk EMV: add quantitative cost/schedule impact fields, make rating/emv computed

Per PMBOK7 / Rita Mulcahy PMP Exam Prep 11th Ed.: EMV = Probability x (monetary/time)
Impact, where Impact must be a real currency/duration value, not a normalized 0-1
score. The existing `impact` field is a qualitative 0-1 severity rating used only
for the probability-impact heat-map (`rating` = probability x impact) — a separate,
non-interchangeable concept from EMV. This migration adds the two quantitative
inputs (cost_impact, schedule_impact_days) needed to compute real EMV, and widens
emv_schedule_days to a decimal since an expected value (probability x days) is
naturally fractional (e.g. 0.3 x 14 = 4.2 days), not an integer count.

Revision ID: c92d4e6f0a17
Revises: b7e2a4f81c33
Create Date: 2026-07-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c92d4e6f0a17'
down_revision: Union[str, None] = 'b7e2a4f81c33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('risks', sa.Column('cost_impact', sa.Numeric(14, 2), nullable=True))
    op.add_column('risks', sa.Column('schedule_impact_days', sa.Integer(), nullable=True))
    op.alter_column(
        'risks', 'emv_schedule_days',
        type_=sa.Numeric(8, 2),
        postgresql_using='emv_schedule_days::numeric(8,2)',
    )


def downgrade() -> None:
    op.alter_column(
        'risks', 'emv_schedule_days',
        type_=sa.Integer(),
        postgresql_using='round(emv_schedule_days)::integer',
    )
    op.drop_column('risks', 'schedule_impact_days')
    op.drop_column('risks', 'cost_impact')
