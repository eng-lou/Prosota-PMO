from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import Period
from app.models.risk import Risk
from app.schemas.risk import RiskCreate, RiskUpdate, _validate_response_strategy
from app.services.reference_codes import next_code


async def _require_live_period(db: AsyncSession, period_id: uuid.UUID) -> None:
    period = await db.get(Period, period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")
    if period.freeze_status != "live":
        raise HTTPException(
            status_code=422,
            detail=f"Period '{period.period_label}' is {period.freeze_status}. Writes to frozen periods are not allowed.",
        )


async def list_risks(
    db: AsyncSession,
    project_id: uuid.UUID,
    period_id: uuid.UUID | None = None,
) -> list[Risk]:
    q = select(Risk).where(Risk.project_id == project_id)
    if period_id is not None:
        q = q.where(Risk.period_id == period_id)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_risk(db: AsyncSession, risk_id: uuid.UUID) -> Risk:
    risk = await db.get(Risk, risk_id)
    if risk is None:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


def _apply_computed_fields(risk: Risk) -> None:
    """Recompute rating and EMV from the risk's current inputs.

    Per PMBOK7 / Rita Mulcahy PMP Exam Prep 11th Ed.: rating is a qualitative,
    unitless heat-map score (probability x impact, both 0-1); EMV is a quantitative
    monetary/schedule figure (probability x cost_most_likely / schedule_most_likely_days,
    in real currency/duration units — the most-likely point of the 3-point estimate;
    min/max are range context only). These are never accepted directly from clients.

    Sign convention (per Ch. 12): cost_most_likely/schedule_most_likely_days are always
    entered as positive magnitudes ("how big is the impact if this happens") — the sign
    is derived from risk_type, not typed in by the user. A threat's cost EMV is negative
    (erodes budget); an opportunity's is positive (adds budget headroom). For schedule
    it's the reverse: a threat ADDS days (positive), an opportunity SAVES days
    (negative) — this asymmetry matches the book's own worked examples exactly.
    """
    risk.rating = (
        risk.probability * risk.impact if risk.probability is not None and risk.impact is not None else None
    )
    risk.rating_residual = (
        risk.probability_residual * risk.impact_residual
        if risk.probability_residual is not None and risk.impact_residual is not None
        else None
    )

    cost_sign = -1 if risk.risk_type == "threat" else 1
    schedule_sign = 1 if risk.risk_type == "threat" else -1

    risk.emv_cost = (
        cost_sign * risk.probability * risk.cost_most_likely
        if risk.probability is not None and risk.cost_most_likely is not None
        else None
    )
    risk.emv_schedule_days = (
        schedule_sign * risk.probability * risk.schedule_most_likely_days
        if risk.probability is not None and risk.schedule_most_likely_days is not None
        else None
    )


async def create_risk(db: AsyncSession, data: RiskCreate) -> Risk:
    await _require_live_period(db, data.period_id)
    code = await next_code(db, Risk, "RSK", data.project_id)
    risk = Risk(**data.model_dump(), code=code)
    _apply_computed_fields(risk)
    db.add(risk)
    await db.commit()
    await db.refresh(risk)
    return risk


async def update_risk(
    db: AsyncSession, risk_id: uuid.UUID, data: RiskUpdate
) -> Risk:
    risk = await get_risk(db, risk_id)
    await _require_live_period(db, risk.period_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(risk, field, value)
    try:
        _validate_response_strategy(risk.risk_type, risk.response_strategy)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    _apply_computed_fields(risk)
    await db.commit()
    await db.refresh(risk)
    return risk


async def delete_risk(db: AsyncSession, risk_id: uuid.UUID) -> None:
    risk = await get_risk(db, risk_id)
    await _require_live_period(db, risk.period_id)
    await db.delete(risk)
    await db.commit()
