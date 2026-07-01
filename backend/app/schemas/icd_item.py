from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

ItemType = Literal["issue", "change", "decision"]
Severity = Literal["low", "medium", "high", "critical"]
ChangeType = Literal["variation", "client_instruction", "omission"]
CcbDecision = Literal["approved", "rejected", "deferred"]
QualityImpact = Literal["high", "medium", "low", "none"]


class IcdItemBase(BaseModel):
    item_type: ItemType
    title: str
    description: str | None = None
    status: str = "open"
    priority: str | None = None
    # raised_by = who raised it; owner = who's resolving it. Distinct people —
    # matches Rita Mulcahy's Issue Log structure ("Raised By" vs "Person Assigned").
    raised_by: str | None = None
    owner: str | None = None
    raised_date: date | None = None
    due_date: date | None = None
    closed_date: date | None = None
    resolution: str | None = None
    last_reviewed_date: date | None = None
    # Change-specific — Integrated Change Control (PMBOK Ch. 4)
    cost_impact: Decimal | None = None
    schedule_impact_days: int | None = None
    change_type: ChangeType | None = None
    ccb_decision: CcbDecision | None = None
    rejection_reason: str | None = None
    contract_reference: str | None = None
    cost_claim: Decimal | None = None
    eot_claim_days: int | None = None
    quality_impact: QualityImpact | None = None
    # Decision-specific
    decision_maker: str | None = None
    required_by: date | None = None
    if_late_consequence: str | None = None
    # Issue-specific
    severity: Severity | None = None

    @model_validator(mode="after")
    def validate_type_fields(self) -> "IcdItemBase":
        change_fields = {
            self.cost_impact, self.schedule_impact_days, self.change_type, self.ccb_decision,
            self.rejection_reason, self.contract_reference, self.cost_claim, self.eot_claim_days,
            self.quality_impact,
        } - {None}
        decision_fields = {self.decision_maker, self.required_by, self.if_late_consequence} - {None}
        issue_fields = {self.severity} - {None}

        if self.item_type != "change" and change_fields:
            raise ValueError(
                "cost_impact, schedule_impact_days, change_type, ccb_decision, rejection_reason, "
                "contract_reference, cost_claim, eot_claim_days, and quality_impact are only valid for changes"
            )
        if self.item_type != "decision" and decision_fields:
            raise ValueError("decision_maker, required_by, and if_late_consequence are only valid for decisions")
        if self.item_type != "issue" and issue_fields:
            raise ValueError("severity is only valid for issues")
        if self.ccb_decision != "rejected" and self.rejection_reason is not None:
            raise ValueError("rejection_reason is only valid when ccb_decision is 'rejected'")
        return self


class IcdItemCreate(IcdItemBase):
    project_id: uuid.UUID
    period_id: uuid.UUID


class IcdItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    raised_by: str | None = None
    owner: str | None = None
    raised_date: date | None = None
    due_date: date | None = None
    closed_date: date | None = None
    resolution: str | None = None
    last_reviewed_date: date | None = None
    cost_impact: Decimal | None = None
    schedule_impact_days: int | None = None
    change_type: ChangeType | None = None
    ccb_decision: CcbDecision | None = None
    rejection_reason: str | None = None
    contract_reference: str | None = None
    cost_claim: Decimal | None = None
    eot_claim_days: int | None = None
    quality_impact: QualityImpact | None = None
    decision_maker: str | None = None
    required_by: date | None = None
    if_late_consequence: str | None = None
    severity: Severity | None = None


class IcdItemResponse(IcdItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    project_id: uuid.UUID
    period_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
