"""risk module phase 1: risk owner, cause/effect/rationale, area

Prototype's General tab has a Cause -> Description -> Effect -> Rationale/
Assumptions risk-statement structure and a Risk Owner field; the scope doc
also has a second categorisation dimension (Theme + Area) alongside the
existing `category` field. See docs/RISK_MODULE_PLAN.md Phase 1.

Revision ID: d4a1e8b3c521
Revises: c92d4e6f0a17
Create Date: 2026-07-01 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4a1e8b3c521'
down_revision: Union[str, None] = 'c92d4e6f0a17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('risks', sa.Column('risk_owner', sa.String(length=255), nullable=True))
    op.add_column('risks', sa.Column('area', sa.String(length=100), nullable=True))
    op.add_column('risks', sa.Column('cause', sa.Text(), nullable=True))
    op.add_column('risks', sa.Column('effect', sa.Text(), nullable=True))
    op.add_column('risks', sa.Column('rationale', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('risks', 'rationale')
    op.drop_column('risks', 'effect')
    op.drop_column('risks', 'cause')
    op.drop_column('risks', 'area')
    op.drop_column('risks', 'risk_owner')
