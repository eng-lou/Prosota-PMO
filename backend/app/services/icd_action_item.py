from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.icd_action_item import IcdActionItem
from app.models.icd_item import IcdItem
from app.schemas.icd_action_item import IcdActionItemCreate, IcdActionItemUpdate
from app.services.icd_item import _require_live_period


async def _next_action_code(db: AsyncSession, icd_item_id: uuid.UUID) -> str:
    """ACT-01, ACT-02... sequential per ICD item (not per project)."""
    stmt = select(func.max(cast(func.split_part(IcdActionItem.code, "-", 2), Integer))).where(
        IcdActionItem.icd_item_id == icd_item_id
    )
    current_max = (await db.execute(stmt)).scalar()
    return f"ACT-{(current_max or 0) + 1:02d}"


async def _get_parent_item(db: AsyncSession, icd_item_id: uuid.UUID) -> IcdItem:
    item = await db.get(IcdItem, icd_item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="ICD item not found")
    return item


async def list_actions(db: AsyncSession, icd_item_id: uuid.UUID) -> list[IcdActionItem]:
    result = await db.execute(
        select(IcdActionItem).where(IcdActionItem.icd_item_id == icd_item_id)
    )
    return list(result.scalars().all())


async def get_action(db: AsyncSession, action_id: uuid.UUID) -> IcdActionItem:
    action = await db.get(IcdActionItem, action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action item not found")
    return action


async def create_action(db: AsyncSession, data: IcdActionItemCreate) -> IcdActionItem:
    item = await _get_parent_item(db, data.icd_item_id)
    await _require_live_period(db, item.period_id)
    code = await _next_action_code(db, data.icd_item_id)
    action = IcdActionItem(**data.model_dump(), code=code)
    db.add(action)
    await db.commit()
    await db.refresh(action)
    return action


async def update_action(
    db: AsyncSession, action_id: uuid.UUID, data: IcdActionItemUpdate
) -> IcdActionItem:
    action = await get_action(db, action_id)
    item = await _get_parent_item(db, action.icd_item_id)
    await _require_live_period(db, item.period_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(action, field, value)
    await db.commit()
    await db.refresh(action)
    return action


async def delete_action(db: AsyncSession, action_id: uuid.UUID) -> None:
    action = await get_action(db, action_id)
    item = await _get_parent_item(db, action.icd_item_id)
    await _require_live_period(db, item.period_id)
    await db.delete(action)
    await db.commit()
