from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ElementType = Literal["fixed", "percentage"]


class CostElementBase(BaseModel):
    element_type: ElementType = "fixed"
    rate: Decimal | None = Field(default=None, ge=0, le=10)  # up to 1000%
    element_group: str | None = None
    description: str
    budget: Decimal | None = None
    forecast: Decimal | None = None
    actuals: Decimal | None = None
    variance: Decimal | None = None
    cpi: Decimal | None = None
    spi: Decimal | None = None
    rev_a_baseline: Decimal | None = None
    cost_per_m2: Decimal | None = None

    @model_validator(mode="after")
    def validate_type_fields(self) -> "CostElementBase":
        if self.element_type == "percentage" and self.rate is None:
            raise ValueError("rate is required for percentage elements")
        if self.element_type == "fixed" and self.rate is not None:
            raise ValueError("rate must be null for fixed elements")
        return self


class CostElementCreate(CostElementBase):
    project_id: uuid.UUID
    period_id: uuid.UUID


class CostElementUpdate(BaseModel):
    element_type: ElementType | None = None
    rate: Decimal | None = Field(default=None, ge=0, le=10)
    element_group: str | None = None
    description: str | None = None
    budget: Decimal | None = None
    forecast: Decimal | None = None
    actuals: Decimal | None = None
    variance: Decimal | None = None
    cpi: Decimal | None = None
    spi: Decimal | None = None
    rev_a_baseline: Decimal | None = None
    cost_per_m2: Decimal | None = None


class CostElementResponse(CostElementBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    project_id: uuid.UUID
    period_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # Populated at query time for percentage elements; None for fixed elements
    computed_budget: Decimal | None = None
    computed_forecast: Decimal | None = None
    computed_actuals: Decimal | None = None
