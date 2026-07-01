"""risk module: key dates + reassessment log

Adds date_raised (matches prototype's "Date Identified"), date_closed,
expected_impact_date (when the risk is expected to occur/materialise, if it
does — Ch.12's risk factor "expected timing for it to occur"), and
last_reviewed_date (matches prototype's "Last Reviewed").

Also adds risk_reassessments — an append-only, timestamped log of "what
changed and why" whenever key figures (probability/impact/status) change,
distinct from the single-point-in-time rating_narrative. Per PMBOK7/Rita
Mulcahy: risk reassessment is a distinct, ongoing Monitor Risks activity,
not a one-off note. Creating a reassessment entry also bumps the parent
risk's last_reviewed_date.

Revision ID: e2a6c81b9f34
Revises: d5f8b2a047e6
Create Date: 2026-07-01 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'e2a6c81b9f34'
down_revision: Union[str, None] = 'd5f8b2a047e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('risks', sa.Column('date_raised', sa.Date(), nullable=True))
    op.add_column('risks', sa.Column('date_closed', sa.Date(), nullable=True))
    op.add_column('risks', sa.Column('expected_impact_date', sa.Date(), nullable=True))
    op.add_column('risks', sa.Column('last_reviewed_date', sa.Date(), nullable=True))

    op.create_table(
        'risk_reassessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('risk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('risks.id'), nullable=False),
        sa.Column('note', sa.Text(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('risk_reassessments')
    op.drop_column('risks', 'last_reviewed_date')
    op.drop_column('risks', 'expected_impact_date')
    op.drop_column('risks', 'date_closed')
    op.drop_column('risks', 'date_raised')
