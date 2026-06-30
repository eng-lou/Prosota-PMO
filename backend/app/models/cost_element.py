from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class CostElement(Base, TimestampMixin):
    __tablename__ = "cost_elements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("periods.id"), nullable=False)
    # 'fixed' = direct budget figure; 'percentage' = rate applied to sum of fixed elements
    element_type: Mapped[str] = mapped_column(String(20), nullable=False, default="fixed")
    # For percentage elements: rate as decimal fraction (0.15 = 15%). NULL for fixed elements.
    # Values are calculated at query time — never stored for percentage elements.
    rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 6))
    element_group: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    budget: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    forecast: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    actuals: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    variance: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    cpi: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    spi: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    rev_a_baseline: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    cost_per_m2: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
