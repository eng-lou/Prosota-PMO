from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CostCommitmentBase(BaseModel):
    po_reference: str | None = None
    description: str
    amount: Decimal


class CostCommitmentCreate(CostCommitmentBase):
    cost_element_id: uuid.UUID


class CostCommitmentUpdate(BaseModel):
    po_reference: str | None = None
    description: str | None = None
    amount: Decimal | None = None


class CostCommitmentResponse(CostCommitmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cost_element_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
