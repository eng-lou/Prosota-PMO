from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RiskReassessmentCreate(BaseModel):
    risk_id: uuid.UUID
    note: str


class RiskReassessmentUpdate(BaseModel):
    note: str


class RiskReassessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    risk_id: uuid.UUID
    note: str
    reviewed_at: datetime
