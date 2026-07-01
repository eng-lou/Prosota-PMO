"""icd decision if_late_consequence field

Revision ID: 63df6368364e
Revises: d601e4a2b7a6
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa


revision = "63df6368364e"
down_revision = "d601e4a2b7a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('icd_items', sa.Column('if_late_consequence', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('icd_items', 'if_late_consequence')
