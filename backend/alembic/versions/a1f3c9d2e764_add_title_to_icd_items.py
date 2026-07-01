"""add title to icd_items

Revision ID: a1f3c9d2e764
Revises: ed3f5af44ff8
Create Date: 2026-07-01 10:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1f3c9d2e764'
down_revision: Union[str, None] = 'ed3f5af44ff8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('icd_items', sa.Column('title', sa.String(length=500), nullable=False))


def downgrade() -> None:
    op.drop_column('icd_items', 'title')
