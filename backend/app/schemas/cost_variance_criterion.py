from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CostVarianceCriterionBase(BaseModel):
    level: int = Field(ge=1, le=4)
    label: str
    min_pct: Decimal | None = None
    max_pct: Decimal | None = None
    description: str | None = None


class CostVarianceCriterionCreate(CostVarianceCriterionBase):
    project_id: uuid.UUID


class CostVarianceCriterionUpdate(BaseModel):
    label: str | None = None
    min_pct: Decimal | None = None
    max_pct: Decimal | None = None
    description: str | None = None


class CostVarianceCriterionResponse(CostVarianceCriterionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
