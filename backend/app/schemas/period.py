from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PeriodCreate(BaseModel):
    project_id: uuid.UUID
    period_label: str
    start_date: date | None = None
    end_date: date | None = None
    cutoff_date: date | None = None
    freeze_status: str = "live"
    baseline_locked_flag: bool = False


class PeriodUpdate(BaseModel):
    period_label: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    cutoff_date: date | None = None
    freeze_status: str | None = None
    baseline_locked_flag: bool | None = None


class PeriodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    period_label: str
    start_date: date | None
    end_date: date | None
    cutoff_date: date | None
    freeze_status: str
    baseline_locked_flag: bool
    created_at: datetime
    updated_at: datetime
