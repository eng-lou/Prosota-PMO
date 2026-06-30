from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

RecordType = Literal["activity", "risk", "cost_element", "issue", "change", "decision"]
LinkType = Literal["causes", "impacts", "mitigates", "relates_to"]


class RecordLinkCreate(BaseModel):
    source_type: RecordType
    source_id: uuid.UUID
    target_type: RecordType
    target_id: uuid.UUID
    link_type: LinkType
    note: str | None = None


class RecordLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_type: str
    source_id: uuid.UUID
    target_type: str
    target_id: uuid.UUID
    link_type: str
    note: str | None
    created_by: uuid.UUID | None
    created_at: datetime
