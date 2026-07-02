"""forecast is the same concept as EAC — drop the manual column, compute instead

Maro caught this: a manually-entered "Forecast" figure duplicates the
already-computed EAC (Estimate at Completion) — both answer "what do we now
expect this line to finally cost". Same mistake class as the earlier
CPI/SPI/cost_per_m2 fixes. forecast is now: EAC once progress has been
assessed, otherwise budget (the best available forecast before any
pct_complete exists).

Revision ID: 17bb0f8d6027
Revises: cc7d1cd00847
Create Date: 2026-07-02

"""
from alembic import op
import sqlalchemy as sa


revision = "17bb0f8d6027"
down_revision = "cc7d1cd00847"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('cost_elements', 'forecast')


def downgrade() -> None:
    op.add_column('cost_elements', sa.Column('forecast', sa.Numeric(14, 2), nullable=True))
