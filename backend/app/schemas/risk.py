from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RiskBase(BaseModel):
    title: str
    category: str | None = None
    status: str = "open"
    probability: Decimal | None = Field(default=None, ge=0, le=1)
    impact: Decimal | None = Field(default=None, ge=0, le=1)
    rating: Decimal | None = Field(default=None, ge=0, le=1)
    emv_cost: Decimal | None = None
    emv_schedule_days: int | None = None
    mitigation_status: str | None = None


class RiskCreate(RiskBase):
    project_id: uuid.UUID
    period_id: uuid.UUID


class RiskUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    status: str | None = None
    probability: Decimal | None = Field(default=None, ge=0, le=1)
    impact: Decimal | None = Field(default=None, ge=0, le=1)
    rating: Decimal | None = Field(default=None, ge=0, le=1)
    emv_cost: Decimal | None = None
    emv_schedule_days: int | None = None
    mitigation_status: str | None = None


class RiskResponse(RiskBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    period_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
