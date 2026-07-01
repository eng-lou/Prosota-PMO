from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RiskProbabilityCriterionBase(BaseModel):
    level: int = Field(ge=1, le=5)
    label: str
    min_probability: Decimal = Field(ge=0, le=1)
    max_probability: Decimal = Field(ge=0, le=1)
    description: str | None = None


class RiskProbabilityCriterionCreate(RiskProbabilityCriterionBase):
    project_id: uuid.UUID


class RiskProbabilityCriterionUpdate(BaseModel):
    label: str | None = None
    min_probability: Decimal | None = Field(default=None, ge=0, le=1)
    max_probability: Decimal | None = Field(default=None, ge=0, le=1)
    description: str | None = None


class RiskProbabilityCriterionResponse(RiskProbabilityCriterionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RiskImpactCriterionBase(BaseModel):
    level: int = Field(ge=1, le=5)
    label: str
    min_cost: Decimal | None = None
    max_cost: Decimal | None = None
    min_schedule_days: int | None = None
    max_schedule_days: int | None = None
    description: str | None = None


class RiskImpactCriterionCreate(RiskImpactCriterionBase):
    project_id: uuid.UUID


class RiskImpactCriterionUpdate(BaseModel):
    label: str | None = None
    min_cost: Decimal | None = None
    max_cost: Decimal | None = None
    min_schedule_days: int | None = None
    max_schedule_days: int | None = None
    description: str | None = None


class RiskImpactCriterionResponse(RiskImpactCriterionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
