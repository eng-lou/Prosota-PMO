from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

RiskType = Literal["threat", "opportunity"]

# Per Rita Mulcahy Ch. 12: threats and opportunities have distinct response strategies,
# sharing only Escalate and Accept. See RISK_MODULE_PLAN.md Phase 2.
THREAT_STRATEGIES = {"avoid", "mitigate", "transfer", "escalate", "accept"}
OPPORTUNITY_STRATEGIES = {"exploit", "enhance", "share", "escalate", "accept"}


def _validate_response_strategy(risk_type: str, response_strategy: str | None) -> None:
    if response_strategy is None:
        return
    valid = THREAT_STRATEGIES if risk_type == "threat" else OPPORTUNITY_STRATEGIES
    if response_strategy not in valid:
        raise ValueError(
            f"'{response_strategy}' is not a valid response strategy for a {risk_type} "
            f"(valid: {sorted(valid)})"
        )


class RiskBase(BaseModel):
    title: str
    # Theme + Area: a simplified two-dimensional Risk Breakdown Structure (RBS).
    category: str | None = None
    area: str | None = None
    status: str = "open"
    risk_owner: str | None = None
    # date_raised matches the prototype's "Date Identified"; last_reviewed_date matches
    # its "Last Reviewed" (also auto-bumped whenever a reassessment is logged — see
    # the generalised Reassessment schema). expected_impact_date is Ch.12's risk factor "expected timing
    # for it to occur in the project life cycle" — when the risk would materialise.
    date_raised: date | None = None
    date_closed: date | None = None
    expected_impact_date: date | None = None
    last_reviewed_date: date | None = None
    # Risk-statement structure: Cause -> title (short description) -> Effect -> Rationale.
    cause: str | None = None
    effect: str | None = None
    rationale: str | None = None
    # threat | opportunity — drives which response strategies are valid and the EMV sign.
    risk_type: RiskType = "threat"
    response_strategy: str | None = None
    # Likelihood (0-1), shared input for both the qualitative heat-map rating and EMV.
    # This pair is the INHERENT (pre-mitigation) assessment.
    probability: Decimal | None = Field(default=None, ge=0, le=1)
    # Qualitative/ordinal severity score (0-1) for the heat-map only — NOT used in EMV.
    impact: Decimal | None = Field(default=None, ge=0, le=1)
    # Residual (post-mitigation target) assessment — same qualitative concept, assuming
    # the planned response has been carried out. rating_residual is computed, like rating.
    probability_residual: Decimal | None = Field(default=None, ge=0, le=1)
    impact_residual: Decimal | None = Field(default=None, ge=0, le=1)
    rating_narrative: str | None = None
    # 3-point (Min/Most Likely/Max) quantitative estimate, in real currency/duration
    # units (always positive magnitudes — EMV's sign is derived from risk_type, not
    # typed in). EMV uses only the most-likely value — the reference material's own
    # worked examples are single-point (PMBOK7 / Rita Mulcahy: EMV = P x Impact).
    cost_min: Decimal | None = None
    cost_most_likely: Decimal | None = None
    cost_max: Decimal | None = None
    schedule_min_days: int | None = None
    schedule_most_likely_days: int | None = None
    schedule_max_days: int | None = None
    mitigation_status: str | None = None
    # Two distinct plans per PMBOK7/Rita Mulcahy: what to do if the risk occurs
    # (contingency) vs what to do if that plan doesn't work (fallback).
    contingency_plan: str | None = None
    fallback_plan: str | None = None

    @model_validator(mode="after")
    def _check_response_strategy(self) -> "RiskBase":
        _validate_response_strategy(self.risk_type, self.response_strategy)
        return self


class RiskCreate(RiskBase):
    project_id: uuid.UUID
    period_id: uuid.UUID


class RiskUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    area: str | None = None
    status: str | None = None
    risk_owner: str | None = None
    date_raised: date | None = None
    date_closed: date | None = None
    expected_impact_date: date | None = None
    last_reviewed_date: date | None = None
    cause: str | None = None
    effect: str | None = None
    rationale: str | None = None
    risk_type: RiskType | None = None
    response_strategy: str | None = None
    probability: Decimal | None = Field(default=None, ge=0, le=1)
    impact: Decimal | None = Field(default=None, ge=0, le=1)
    probability_residual: Decimal | None = Field(default=None, ge=0, le=1)
    impact_residual: Decimal | None = Field(default=None, ge=0, le=1)
    rating_narrative: str | None = None
    cost_min: Decimal | None = None
    cost_most_likely: Decimal | None = None
    cost_max: Decimal | None = None
    schedule_min_days: int | None = None
    schedule_most_likely_days: int | None = None
    schedule_max_days: int | None = None
    mitigation_status: str | None = None
    contingency_plan: str | None = None
    fallback_plan: str | None = None


class RiskResponse(RiskBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    project_id: uuid.UUID
    period_id: uuid.UUID
    # Computed server-side — never accepted as input. rating = probability x impact
    # (qualitative heat-map score); rating_residual is the same, for the residual pair.
    # emv_cost/emv_schedule_days = probability x cost_most_likely/schedule_most_likely_days,
    # signed per risk_type (real EMV).
    rating: Decimal | None = None
    rating_residual: Decimal | None = None
    emv_cost: Decimal | None = None
    emv_schedule_days: Decimal | None = None
    created_at: datetime
    updated_at: datetime
