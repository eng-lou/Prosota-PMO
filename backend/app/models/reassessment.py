from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Reassessment(Base):
    """An append-only-by-default, timestamped log entry recording what changed
    about a record and why (e.g. probability/impact revised, priority
    escalated, cost re-forecast) — distinct from a single current-state
    narrative field. Polymorphic (record_type, record_id) — mirrors
    `record_links`' proven pattern rather than per-parent FK columns, since
    this is now the third module (Risk, ICD, Cost) to use the identical
    user-prompted reassessment mechanism. Editable/deletable — a working log,
    not a strict audit trail."""

    __tablename__ = "reassessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # risk | icd_item | cost_element
    record_type: Mapped[str] = mapped_column(String(50), nullable=False)
    record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
