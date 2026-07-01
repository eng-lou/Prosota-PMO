from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RiskReassessment(Base):
    """An append-only, timestamped log entry recording what changed about a risk
    and why (e.g. probability/impact revised, risk closed) — distinct from
    `rating_narrative`, which is a single current-state explanation, not a history.
    Per PMBOK7/Rita Mulcahy: risk reassessment is an ongoing Monitor Risks activity.
    No update/delete — it's a historical record, not an editable field."""

    __tablename__ = "risk_reassessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("risks.id"), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
