from __future__ import annotations

import uuid
from datetime import date as date_type

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.icd_item import IcdItem
from app.models.icd_reassessment import IcdReassessment
from app.schemas.icd_reassessment import IcdReassessmentCreate, IcdReassessmentUpdate
from app.services.icd_item import _require_live_period


async def list_reassessments(db: AsyncSession, icd_item_id: uuid.UUID) -> list[IcdReassessment]:
    result = await db.execute(
        select(IcdReassessment)
        .where(IcdReassessment.icd_item_id == icd_item_id)
        .order_by(IcdReassessment.reviewed_at.desc())
    )
    return list(result.scalars().all())


async def get_reassessment(db: AsyncSession, reassessment_id: uuid.UUID) -> IcdReassessment:
    entry = await db.get(IcdReassessment, reassessment_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Reassessment not found")
    return entry


async def create_reassessment(db: AsyncSession, data: IcdReassessmentCreate) -> IcdReassessment:
    """Logging a reassessment is itself a review event, so it also bumps the
    parent item's last_reviewed_date — mirrors the Risk module's Monitor Risks
    pattern, applied here to issues/changes/decisions."""
    item = await db.get(IcdItem, data.icd_item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="ICD item not found")
    await _require_live_period(db, item.period_id)

    entry = IcdReassessment(icd_item_id=data.icd_item_id, note=data.note)
    db.add(entry)
    item.last_reviewed_date = date_type.today()
    await db.commit()
    await db.refresh(entry)
    return entry


async def update_reassessment(
    db: AsyncSession, reassessment_id: uuid.UUID, data: IcdReassessmentUpdate
) -> IcdReassessment:
    entry = await get_reassessment(db, reassessment_id)
    item = await db.get(IcdItem, entry.icd_item_id)
    if item is not None:
        await _require_live_period(db, item.period_id)
    entry.note = data.note
    await db.commit()
    await db.refresh(entry)
    return entry


async def delete_reassessment(db: AsyncSession, reassessment_id: uuid.UUID) -> None:
    entry = await get_reassessment(db, reassessment_id)
    item = await db.get(IcdItem, entry.icd_item_id)
    if item is not None:
        await _require_live_period(db, item.period_id)
    await db.delete(entry)
    await db.commit()
