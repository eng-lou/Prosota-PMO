"""cost element general field gaps

Revision ID: 3fd361dbc813
Revises: b1094c80580b
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa


revision = "3fd361dbc813"
down_revision = "b1094c80580b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('cost_elements', sa.Column('cost_owner', sa.String(length=255), nullable=True))
    op.add_column('cost_elements', sa.Column('status', sa.String(length=20), nullable=True))
    op.add_column('cost_elements', sa.Column('scope_note', sa.Text(), nullable=True))
    op.add_column('cost_elements', sa.Column('variance_commentary', sa.Text(), nullable=True))
    op.add_column('cost_elements', sa.Column('qs_signoff_name', sa.String(length=255), nullable=True))
    op.add_column('cost_elements', sa.Column('qs_signoff_date', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('cost_elements', 'qs_signoff_date')
    op.drop_column('cost_elements', 'qs_signoff_name')
    op.drop_column('cost_elements', 'variance_commentary')
    op.drop_column('cost_elements', 'scope_note')
    op.drop_column('cost_elements', 'status')
    op.drop_column('cost_elements', 'cost_owner')
