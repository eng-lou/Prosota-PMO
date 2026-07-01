"""fix: widen risks.mitigation_status from varchar(50) to text

Real usage (a manual click-through by the founder) immediately hit a
"value too long" error entering a realistic mitigation status paragraph —
a genuine schema bug, not a validation the user should have to work around.
mitigation_status is a narrative field like contingency_plan/fallback_plan/
rating_narrative, not a short enum-like status code, so it should never
have been capped at 50 characters.

Revision ID: d5f8b2a047e6
Revises: c1e7a93f5d84
Create Date: 2026-07-01 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd5f8b2a047e6'
down_revision: Union[str, None] = 'c1e7a93f5d84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('risks', 'mitigation_status', type_=sa.Text())


def downgrade() -> None:
    op.alter_column('risks', 'mitigation_status', type_=sa.String(length=50))
