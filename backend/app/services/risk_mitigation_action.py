from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.risk import Risk
from app.models.risk_mitigation_action import RiskMitigationAction
from app.schemas.risk_mitigation_action import (
    RiskMitigationActionCreate,
    RiskMitigationActionUpdate,
)
from app.services.risk import _require_live_period


async def _next_action_code(db: AsyncSession, risk_id: uuid.UUID) -> str:
    """MA-01, MA-02... sequential per risk (not per project) — matches the prototype."""
    stmt = select(func.max(cast(func.split_part(RiskMitigationAction.code, "-", 2), Integer))).where(
        RiskMitigationAction.risk_id == risk_id
    )
    current_max = (await db.execute(stmt)).scalar()
    return f"MA-{(current_max or 0) + 1:02d}"


async def _get_parent_risk(db: AsyncSession, risk_id: uuid.UUID) -> Risk:
    risk = await db.get(Risk, risk_id)
    if risk is None:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


async def list_actions(db: AsyncSession, risk_id: uuid.UUID) -> list[RiskMitigationAction]:
    result = await db.execute(
        select(RiskMitigationAction).where(RiskMitigationAction.risk_id == risk_id)
    )
    return list(result.scalars().all())


async def get_action(db: AsyncSession, action_id: uuid.UUID) -> RiskMitigationAction:
    action = await db.get(RiskMitigationAction, action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Mitigation action not found")
    return action


async def create_action(
    db: AsyncSession, data: RiskMitigationActionCreate
) -> RiskMitigationAction:
    risk = await _get_parent_risk(db, data.risk_id)
    await _require_live_period(db, risk.period_id)
    code = await _next_action_code(db, data.risk_id)
    action = RiskMitigationAction(**data.model_dump(), code=code)
    db.add(action)
    await db.commit()
    await db.refresh(action)
    return action


async def update_action(
    db: AsyncSession, action_id: uuid.UUID, data: RiskMitigationActionUpdate
) -> RiskMitigationAction:
    action = await get_action(db, action_id)
    risk = await _get_parent_risk(db, action.risk_id)
    await _require_live_period(db, risk.period_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(action, field, value)
    await db.commit()
    await db.refresh(action)
    return action


async def delete_action(db: AsyncSession, action_id: uuid.UUID) -> None:
    action = await get_action(db, action_id)
    risk = await _get_parent_risk(db, action.risk_id)
    await _require_live_period(db, risk.period_id)
    await db.delete(action)
    await db.commit()
