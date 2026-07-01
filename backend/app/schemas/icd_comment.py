from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IcdCommentCreate(BaseModel):
    icd_item_id: uuid.UUID
    body: str


class IcdCommentUpdate(BaseModel):
    body: str


class IcdCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    icd_item_id: uuid.UUID
    author_id: uuid.UUID
    author_name: str
    body: str
    created_at: datetime
    updated_at: datetime
