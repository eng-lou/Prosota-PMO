from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.icd_item import IcdItem
from app.models.period import Period
from app.schemas.icd_item import IcdItemCreate, IcdItemUpdate
from app.services.reference_codes import next_code

_CODE_PREFIXES = {"issue": "ISS", "change": "CHA", "decision": "DEC"}


async def _require_live_period(db: AsyncSession, period_id: uuid.UUID) -> None:
    period = await db.get(Period, period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")
    if period.freeze_status != "live":
        raise HTTPException(
            status_code=422,
            detail=f"Period '{period.period_label}' is {period.freeze_status}. Writes to frozen periods are not allowed.",
        )


async def list_icd_items(
    db: AsyncSession,
    project_id: uuid.UUID,
    period_id: uuid.UUID | None = None,
    item_type: str | None = None,
) -> list[IcdItem]:
    q = select(IcdItem).where(IcdItem.project_id == project_id)
    if period_id is not None:
        q = q.where(IcdItem.period_id == period_id)
    if item_type is not None:
        q = q.where(IcdItem.item_type == item_type)
    return list((await db.execute(q)).scalars().all())


async def get_icd_item(db: AsyncSession, item_id: uuid.UUID) -> IcdItem:
    item = await db.get(IcdItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="ICD item not found")
    return item


async def create_icd_item(db: AsyncSession, data: IcdItemCreate) -> IcdItem:
    await _require_live_period(db, data.period_id)
    code = await next_code(
        db, IcdItem, _CODE_PREFIXES[data.item_type], data.project_id,
        extra_filter=IcdItem.item_type == data.item_type,
    )
    item = IcdItem(**data.model_dump(), code=code)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_icd_item(
    db: AsyncSession, item_id: uuid.UUID, data: IcdItemUpdate
) -> IcdItem:
    item = await get_icd_item(db, item_id)
    await _require_live_period(db, item.period_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def delete_icd_item(db: AsyncSession, item_id: uuid.UUID) -> None:
    item = await get_icd_item(db, item_id)
    await _require_live_period(db, item.period_id)
    await db.delete(item)
    await db.commit()
