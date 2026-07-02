"""generalize reassessment log into one polymorphic table

Third use of the same "user-prompted reassessment log" pattern (Risk, then
ICD, now Cost) — per Maro's decision, generalised now rather than copied a
third time. New `reassessments` table mirrors `record_links`' proven
polymorphic (record_type, record_id) pattern rather than per-parent FK
columns. Existing risk_reassessments/icd_reassessments rows are migrated
across, then the old tables are dropped.

Revision ID: cc7d1cd00847
Revises: fad42d2dc977
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "cc7d1cd00847"
down_revision = "fad42d2dc977"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reassessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("record_type", sa.String(length=50), nullable=False),
        sa.Column("record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    conn = op.get_bind()
    conn.execute(sa.text("""
        INSERT INTO reassessments (id, record_type, record_id, note, reviewed_at)
        SELECT id, 'risk', risk_id, note, reviewed_at FROM risk_reassessments
    """))
    conn.execute(sa.text("""
        INSERT INTO reassessments (id, record_type, record_id, note, reviewed_at)
        SELECT id, 'icd_item', icd_item_id, note, reviewed_at FROM icd_reassessments
    """))

    op.drop_table("risk_reassessments")
    op.drop_table("icd_reassessments")


def downgrade() -> None:
    op.create_table(
        "risk_reassessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("risk_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("risks.id"), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "icd_reassessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("icd_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("icd_items.id"), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    conn = op.get_bind()
    conn.execute(sa.text("""
        INSERT INTO risk_reassessments (id, risk_id, note, reviewed_at)
        SELECT id, record_id, note, reviewed_at FROM reassessments WHERE record_type = 'risk'
    """))
    conn.execute(sa.text("""
        INSERT INTO icd_reassessments (id, icd_item_id, note, reviewed_at)
        SELECT id, record_id, note, reviewed_at FROM reassessments WHERE record_type = 'icd_item'
    """))

    op.drop_table("reassessments")
