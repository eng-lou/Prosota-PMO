from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.period import Period
from app.schemas.activity import ActivityCreate, ActivityUpdate


async def _require_live_period(db: AsyncSession, period_id: uuid.UUID) -> None:
    period = await db.get(Period, period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")
    if period.freeze_status != "live":
        raise HTTPException(
            status_code=422,
            detail=f"Period '{period.period_label}' is {period.freeze_status}. Writes to frozen periods are not allowed.",
        )


async def list_activities(
    db: AsyncSession,
    project_id: uuid.UUID,
    period_id: uuid.UUID | None = None,
) -> list[Activity]:
    q = select(Activity).where(Activity.project_id == project_id)
    if period_id is not None:
        q = q.where(Activity.period_id == period_id)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_activity(db: AsyncSession, activity_id: uuid.UUID) -> Activity:
    activity = await db.get(Activity, activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


async def create_activity(db: AsyncSession, data: ActivityCreate) -> Activity:
    await _require_live_period(db, data.period_id)
    activity = Activity(**data.model_dump())
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def update_activity(
    db: AsyncSession, activity_id: uuid.UUID, data: ActivityUpdate
) -> Activity:
    activity = await get_activity(db, activity_id)
    await _require_live_period(db, activity.period_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)
    await db.commit()
    await db.refresh(activity)
    return activity


async def delete_activity(db: AsyncSession, activity_id: uuid.UUID) -> None:
    activity = await get_activity(db, activity_id)
    await _require_live_period(db, activity.period_id)
    await db.delete(activity)
    await db.commit()
