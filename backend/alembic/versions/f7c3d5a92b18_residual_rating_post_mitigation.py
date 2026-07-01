"""risk module phase 3: residual (post-mitigation) rating

The existing probability/impact/rating fields represent the inherent
(pre-mitigation) assessment. Adds a parallel residual (post-mitigation
target) probability/impact/rating, per the prototype's Qualitative Analysis
tab (Pre-Mitigation vs Post-Mitigation side-by-side comparison) and PMBOK7 /
Rita Mulcahy's residual risk concept. See docs/RISK_MODULE_PLAN.md Phase 3.

Revision ID: f7c3d5a92b18
Revises: e6f2b9d47a83
Create Date: 2026-07-01 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f7c3d5a92b18'
down_revision: Union[str, None] = 'e6f2b9d47a83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('risks', sa.Column('probability_residual', sa.Numeric(5, 2), nullable=True))
    op.add_column('risks', sa.Column('impact_residual', sa.Numeric(5, 2), nullable=True))
    op.add_column('risks', sa.Column('rating_residual', sa.Numeric(5, 2), nullable=True))
    op.add_column('risks', sa.Column('rating_narrative', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('risks', 'rating_narrative')
    op.drop_column('risks', 'rating_residual')
    op.drop_column('risks', 'impact_residual')
    op.drop_column('risks', 'probability_residual')
