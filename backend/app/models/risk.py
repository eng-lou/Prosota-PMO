from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Risk(Base, TimestampMixin):
    __tablename__ = "risks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("periods.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    probability: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    impact: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    rating: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    emv_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    emv_schedule_days: Mapped[int | None] = mapped_column(Integer)
    mitigation_status: Mapped[str | None] = mapped_column(String(50))
