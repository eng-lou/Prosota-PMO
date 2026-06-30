from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ActivityBase(BaseModel):
    task_name: str
    wbs_path: str | None = None
    start: date | None = None
    finish: date | None = None
    bl_start: date | None = None
    bl_finish: date | None = None
    variance_days: int | None = None
    pct_complete: Decimal | None = Field(default=None, ge=0, le=100)
    total_float: int | None = None
    is_critical: bool = False


class ActivityCreate(ActivityBase):
    project_id: uuid.UUID
    period_id: uuid.UUID


class ActivityUpdate(BaseModel):
    task_name: str | None = None
    wbs_path: str | None = None
    start: date | None = None
    finish: date | None = None
    bl_start: date | None = None
    bl_finish: date | None = None
    variance_days: int | None = None
    pct_complete: Decimal | None = Field(default=None, ge=0, le=100)
    total_float: int | None = None
    is_critical: bool | None = None


class ActivityResponse(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    period_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
