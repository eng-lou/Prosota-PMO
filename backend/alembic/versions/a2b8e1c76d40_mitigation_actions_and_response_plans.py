"""risk module phase 4: mitigation actions sub-list, contingency/fallback plans

New risk_mitigation_actions table — a one-to-many sub-record (own code like
"MA-01", owner, due date, status, % complete), matching the prototype's
Mitigation & Response tab, plus contingency_plan/fallback_plan text fields
on the risk itself (two distinct concepts per PMBOK7/Rita Mulcahy: what to do
if the risk occurs vs what to do if that plan doesn't work).
See docs/RISK_MODULE_PLAN.md Phase 4.

Revision ID: a2b8e1c76d40
Revises: f7c3d5a92b18
Create Date: 2026-07-01 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a2b8e1c76d40'
down_revision: Union[str, None] = 'f7c3d5a92b18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('risks', sa.Column('contingency_plan', sa.Text(), nullable=True))
    op.add_column('risks', sa.Column('fallback_plan', sa.Text(), nullable=True))

    op.create_table(
        'risk_mitigation_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('risk_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('risks.id'), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('owner', sa.String(length=255), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='not_started'),
        sa.Column('pct_complete', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('risk_id', 'code', name='uq_risk_mitigation_actions_risk_code'),
    )


def downgrade() -> None:
    op.drop_table('risk_mitigation_actions')
    op.drop_column('risks', 'fallback_plan')
    op.drop_column('risks', 'contingency_plan')
