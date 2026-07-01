"""icd module phase 1: fill Issue Log field gaps

Rita Mulcahy Ch. 6, Figure 6.7 gives the canonical Issue Log structure:
"Issue # | Issue | Date Added | Raised By | Person Assigned | Resolution Due
Date | Status | Date Resolved | Resolution". Our icd_items had title/status/
owner/raised_date/closed_date but was missing description, raised_by
(distinct from owner, who resolves it), due_date, and resolution — all
explicitly named in the book's own structure. See docs/ICD_MODULE_PLAN.md
Phase 1.

Revision ID: f4b8e2c917a5
Revises: e2a6c81b9f34
Create Date: 2026-07-01 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f4b8e2c917a5'
down_revision: Union[str, None] = 'e2a6c81b9f34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('icd_items', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('icd_items', sa.Column('raised_by', sa.String(length=255), nullable=True))
    op.add_column('icd_items', sa.Column('due_date', sa.Date(), nullable=True))
    op.add_column('icd_items', sa.Column('resolution', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('icd_items', 'resolution')
    op.drop_column('icd_items', 'due_date')
    op.drop_column('icd_items', 'raised_by')
    op.drop_column('icd_items', 'description')
