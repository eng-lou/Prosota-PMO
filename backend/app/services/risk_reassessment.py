from __future__ import annotations

import uuid
from datetime import date as date_type

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.risk import Risk
from app.models.risk_reassessment import RiskReassessment
from app.schemas.risk_reassessment import RiskReassessmentCreate, RiskReassessmentUpdate
from app.services.risk import _require_live_period


async def list_reassessments(db: AsyncSession, risk_id: uuid.UUID) -> list[RiskReassessment]:
    result = await db.execute(
        select(RiskReassessment)
        .where(RiskReassessment.risk_id == risk_id)
        .order_by(RiskReassessment.reviewed_at.desc())
    )
    return list(result.scalars().all())


async def get_reassessment(db: AsyncSession, reassessment_id: uuid.UUID) -> RiskReassessment:
    entry = await db.get(RiskReassessment, reassessment_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Reassessment not found")
    return entry


async def create_reassessment(
    db: AsyncSession, data: RiskReassessmentCreate
) -> RiskReassessment:
    """Logging a reassessment is itself a review event, so it also bumps the
    parent risk's last_reviewed_date — per PMBOK7/Rita Mulcahy's Monitor Risks
    concept of ongoing risk reassessment, distinct from the one-off rating_narrative."""
    risk = await db.get(Risk, data.risk_id)
    if risk is None:
        raise HTTPException(status_code=404, detail="Risk not found")
    await _require_live_period(db, risk.period_id)

    entry = RiskReassessment(risk_id=data.risk_id, note=data.note)
    db.add(entry)
    risk.last_reviewed_date = date_type.today()
    await db.commit()
    await db.refresh(entry)
    return entry


async def update_reassessment(
    db: AsyncSession, reassessment_id: uuid.UUID, data: RiskReassessmentUpdate
) -> RiskReassessment:
    entry = await get_reassessment(db, reassessment_id)
    risk = await db.get(Risk, entry.risk_id)
    if risk is not None:
        await _require_live_period(db, risk.period_id)
    entry.note = data.note
    await db.commit()
    await db.refresh(entry)
    return entry


async def delete_reassessment(db: AsyncSession, reassessment_id: uuid.UUID) -> None:
    entry = await get_reassessment(db, reassessment_id)
    risk = await db.get(Risk, entry.risk_id)
    if risk is not None:
        await _require_live_period(db, risk.period_id)
    await db.delete(entry)
    await db.commit()
