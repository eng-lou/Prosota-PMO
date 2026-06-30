from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Activity(Base, TimestampMixin):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("periods.id"), nullable=False)
    task_name: Mapped[str] = mapped_column(String(500), nullable=False)
    wbs_path: Mapped[str | None] = mapped_column(String(500))
    start: Mapped[date | None] = mapped_column(Date)
    finish: Mapped[date | None] = mapped_column(Date)
    bl_start: Mapped[date | None] = mapped_column(Date)
    bl_finish: Mapped[date | None] = mapped_column(Date)
    variance_days: Mapped[int | None] = mapped_column(Integer)
    pct_complete: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    total_float: Mapped[int | None] = mapped_column(Integer)
    is_critical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
