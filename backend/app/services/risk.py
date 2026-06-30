from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import Period
from app.models.risk import Risk
from app.schemas.risk import RiskCreate, RiskUpdate


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


async def create_risk(db: AsyncSession, data: RiskCreate) -> Risk:
    await _require_live_period(db, data.period_id)
    risk = Risk(**data.model_dump())
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
    await db.commit()
    await db.refresh(risk)
    return risk


async def delete_risk(db: AsyncSession, risk_id: uuid.UUID) -> None:
    risk = await get_risk(db, risk_id)
    await _require_live_period(db, risk.period_id)
    await db.delete(risk)
    await db.commit()
