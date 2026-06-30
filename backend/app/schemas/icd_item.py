from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

ItemType = Literal["issue", "change", "decision"]
Severity = Literal["low", "medium", "high", "critical"]


class IcdItemBase(BaseModel):
    item_type: ItemType
    status: str = "open"
    priority: str | None = None
    owner: str | None = None
    raised_date: date | None = None
    closed_date: date | None = None
    # Change-specific
    cost_impact: Decimal | None = None
    schedule_impact_days: int | None = None
    # Decision-specific
    decision_maker: str | None = None
    required_by: date | None = None
    # Issue-specific
    severity: Severity | None = None

    @model_validator(mode="after")
    def validate_type_fields(self) -> "IcdItemBase":
        change_fields = {self.cost_impact, self.schedule_impact_days} - {None}
        decision_fields = {self.decision_maker, self.required_by} - {None}
        issue_fields = {self.severity} - {None}

        if self.item_type != "change" and change_fields:
            raise ValueError("cost_impact and schedule_impact_days are only valid for changes")
        if self.item_type != "decision" and decision_fields:
            raise ValueError("decision_maker and required_by are only valid for decisions")
        if self.item_type != "issue" and issue_fields:
            raise ValueError("severity is only valid for issues")
        return self


class IcdItemCreate(IcdItemBase):
    project_id: uuid.UUID
    period_id: uuid.UUID


class IcdItemUpdate(BaseModel):
    status: str | None = None
    priority: str | None = None
    owner: str | None = None
    raised_date: date | None = None
    closed_date: date | None = None
    cost_impact: Decimal | None = None
    schedule_impact_days: int | None = None
    decision_maker: str | None = None
    required_by: date | None = None
    severity: Severity | None = None


class IcdItemResponse(IcdItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    period_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
