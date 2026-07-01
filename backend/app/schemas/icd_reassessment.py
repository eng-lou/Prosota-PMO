from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IcdReassessmentCreate(BaseModel):
    icd_item_id: uuid.UUID
    note: str


class IcdReassessmentUpdate(BaseModel):
    note: str


class IcdReassessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    icd_item_id: uuid.UUID
    note: str
    reviewed_at: datetime
