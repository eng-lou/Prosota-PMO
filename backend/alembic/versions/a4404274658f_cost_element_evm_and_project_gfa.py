"""cost element EVM (pct_complete, drop dead cpi/spi) and project GFA/space count

Revision ID: a4404274658f
Revises: 3fd361dbc813
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa


revision = "a4404274658f"
down_revision = "3fd361dbc813"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('cost_elements', sa.Column('pct_complete', sa.Integer(), nullable=True))
    # cpi/spi were dead unused columns (removed from manual entry previously, nothing ever
    # computed them); variance was a manual figure that's fully derivable from budget minus
    # rev_a_baseline. All three become query-time computed values, like computed_budget.
    op.drop_column('cost_elements', 'cpi')
    op.drop_column('cost_elements', 'spi')
    op.drop_column('cost_elements', 'variance')
    # cost_per_m2 was manual free-text entry — same "computed field exposed as input"
    # mistake class as EMV/CPI/SPI; now computed from budget / project.gfa_m2.
    op.drop_column('cost_elements', 'cost_per_m2')

    op.add_column('projects', sa.Column('gfa_m2', sa.Numeric(10, 2), nullable=True))
    op.add_column('projects', sa.Column('space_count', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('projects', 'space_count')
    op.drop_column('projects', 'gfa_m2')

    op.add_column('cost_elements', sa.Column('cost_per_m2', sa.Numeric(10, 2), nullable=True))
    op.add_column('cost_elements', sa.Column('variance', sa.Numeric(14, 2), nullable=True))
    op.add_column('cost_elements', sa.Column('spi', sa.Numeric(8, 4), nullable=True))
    op.add_column('cost_elements', sa.Column('cpi', sa.Numeric(8, 4), nullable=True))
    op.drop_column('cost_elements', 'pct_complete')
