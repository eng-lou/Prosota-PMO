"""icd change control fields

Revision ID: ce2b0dd1ef9f
Revises: f4b8e2c917a5
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa


revision = "ce2b0dd1ef9f"
down_revision = "f4b8e2c917a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('icd_items', sa.Column('change_type', sa.String(length=30), nullable=True))
    op.add_column('icd_items', sa.Column('ccb_decision', sa.String(length=20), nullable=True))
    op.add_column('icd_items', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.add_column('icd_items', sa.Column('contract_reference', sa.Text(), nullable=True))
    op.add_column('icd_items', sa.Column('cost_claim', sa.Numeric(14, 2), nullable=True))
    op.add_column('icd_items', sa.Column('eot_claim_days', sa.Integer(), nullable=True))
    op.add_column('icd_items', sa.Column('quality_impact', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('icd_items', 'quality_impact')
    op.drop_column('icd_items', 'eot_claim_days')
    op.drop_column('icd_items', 'cost_claim')
    op.drop_column('icd_items', 'contract_reference')
    op.drop_column('icd_items', 'rejection_reason')
    op.drop_column('icd_items', 'ccb_decision')
    op.drop_column('icd_items', 'change_type')
