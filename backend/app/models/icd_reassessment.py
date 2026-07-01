from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class IcdReassessment(Base):
    """An append-only, timestamped log entry recording what changed about an
    issue/change/decision and why (e.g. priority escalated, CCB decision made)
    — distinct from `resolution`, which is a single current-state field, not a
    history. Editable/deletable, like Risk's reassessment log — a working log,
    not a strict audit trail."""

    __tablename__ = "icd_reassessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    icd_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("icd_items.id"), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
