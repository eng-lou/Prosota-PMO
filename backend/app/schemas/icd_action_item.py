from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class IcdActionItemBase(BaseModel):
    description: str
    owner: str | None = None
    due_date: date | None = None
    status: str = "not_started"
    pct_complete: int = Field(default=0, ge=0, le=100)


class IcdActionItemCreate(IcdActionItemBase):
    icd_item_id: uuid.UUID


class IcdActionItemUpdate(BaseModel):
    description: str | None = None
    owner: str | None = None
    due_date: date | None = None
    status: str | None = None
    pct_complete: int | None = Field(default=None, ge=0, le=100)


class IcdActionItemResponse(IcdActionItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    icd_item_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
