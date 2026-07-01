from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class IcdItem(Base, TimestampMixin):
    __tablename__ = "icd_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("periods.id"), nullable=False)
    # Discriminator: issue | change | decision
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Shared fields
    # Human-readable reference (e.g. "ISS-0001"/"CHA-0001"/"DEC-0001"), auto-generated per
    # project per sub-type. Never reused.
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    priority: Mapped[str | None] = mapped_column(String(20))
    owner: Mapped[str | None] = mapped_column(String(255))
    raised_date: Mapped[date | None] = mapped_column(Date)
    closed_date: Mapped[date | None] = mapped_column(Date)

    # Change-specific
    cost_impact: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    schedule_impact_days: Mapped[int | None] = mapped_column(Integer)

    # Decision-specific
    decision_maker: Mapped[str | None] = mapped_column(String(255))
    required_by: Mapped[date | None] = mapped_column(Date)

    # Issue-specific
    severity: Mapped[str | None] = mapped_column(String(20))  # low | medium | high | critical
