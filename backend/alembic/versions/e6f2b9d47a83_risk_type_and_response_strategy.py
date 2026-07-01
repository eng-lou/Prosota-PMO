"""risk module phase 2: threat vs opportunity, response strategy

Per Rita Mulcahy Ch. 12: every risk is a threat or an opportunity, and each
has its own distinct set of response strategies (threats: Avoid/Mitigate/
Transfer/Escalate/Accept; opportunities: Exploit/Enhance/Share/Escalate/
Accept). The prototype's single response dropdown mixed both — not copied.
See docs/RISK_MODULE_PLAN.md Phase 2.

Revision ID: e6f2b9d47a83
Revises: d4a1e8b3c521
Create Date: 2026-07-01 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e6f2b9d47a83'
down_revision: Union[str, None] = 'd4a1e8b3c521'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('risks', sa.Column('risk_type', sa.String(length=20), nullable=False, server_default='threat'))
    op.alter_column('risks', 'risk_type', server_default=None)
    op.add_column('risks', sa.Column('response_strategy', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('risks', 'response_strategy')
    op.drop_column('risks', 'risk_type')
