"""add human-readable code to risks, cost_elements, icd_items

Revision ID: b7e2a4f81c33
Revises: a1f3c9d2e764
Create Date: 2026-07-01 11:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7e2a4f81c33'
down_revision: Union[str, None] = 'a1f3c9d2e764'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CODE_PREFIXES = {"issue": "ISS", "change": "CHA", "decision": "DEC"}


def upgrade() -> None:
    op.add_column('risks', sa.Column('code', sa.String(length=20), nullable=True))
    op.add_column('cost_elements', sa.Column('code', sa.String(length=20), nullable=True))
    op.add_column('icd_items', sa.Column('code', sa.String(length=20), nullable=True))

    # Backfill any pre-existing rows (created before codes existed) in creation order,
    # numbered per project (and per item_type for icd_items).
    connection = op.get_bind()

    connection.execute(sa.text("""
        UPDATE risks r SET code = 'RSK-' || LPAD(sub.rn::text, 4, '0')
        FROM (SELECT id, row_number() OVER (PARTITION BY project_id ORDER BY created_at) AS rn FROM risks) sub
        WHERE r.id = sub.id
    """))
    connection.execute(sa.text("""
        UPDATE cost_elements c SET code = 'CST-' || LPAD(sub.rn::text, 4, '0')
        FROM (SELECT id, row_number() OVER (PARTITION BY project_id ORDER BY created_at) AS rn FROM cost_elements) sub
        WHERE c.id = sub.id
    """))
    for item_type, prefix in _CODE_PREFIXES.items():
        connection.execute(sa.text(f"""
            UPDATE icd_items i SET code = '{prefix}-' || LPAD(sub.rn::text, 4, '0')
            FROM (
                SELECT id, row_number() OVER (PARTITION BY project_id ORDER BY created_at) AS rn
                FROM icd_items WHERE item_type = '{item_type}'
            ) sub
            WHERE i.id = sub.id AND i.item_type = '{item_type}'
        """))

    op.alter_column('risks', 'code', nullable=False)
    op.alter_column('cost_elements', 'code', nullable=False)
    op.alter_column('icd_items', 'code', nullable=False)

    op.create_unique_constraint('uq_risks_project_code', 'risks', ['project_id', 'code'])
    op.create_unique_constraint('uq_cost_elements_project_code', 'cost_elements', ['project_id', 'code'])
    op.create_unique_constraint('uq_icd_items_project_code', 'icd_items', ['project_id', 'code'])


def downgrade() -> None:
    op.drop_constraint('uq_icd_items_project_code', 'icd_items', type_='unique')
    op.drop_constraint('uq_cost_elements_project_code', 'cost_elements', type_='unique')
    op.drop_constraint('uq_risks_project_code', 'risks', type_='unique')
    op.drop_column('icd_items', 'code')
    op.drop_column('cost_elements', 'code')
    op.drop_column('risks', 'code')
