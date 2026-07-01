from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Dimension = Literal["priority", "severity", "quality_impact"]


class IcdCriterionBase(BaseModel):
    level: int = Field(ge=1, le=4)
    label: str
    description: str | None = None


class IcdCriterionCreate(IcdCriterionBase):
    project_id: uuid.UUID
    dimension: Dimension


class IcdCriterionUpdate(BaseModel):
    label: str | None = None
    description: str | None = None


class IcdCriterionResponse(IcdCriterionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    dimension: Dimension
    created_at: datetime
    updated_at: datetime
