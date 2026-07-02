"""cost element last_reviewed_date

Revision ID: fad42d2dc977
Revises: e2fde8c5a226
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa


revision = "fad42d2dc977"
down_revision = "e2fde8c5a226"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('cost_elements', sa.Column('last_reviewed_date', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('cost_elements', 'last_reviewed_date')
