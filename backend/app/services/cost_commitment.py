from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cost_commitment import CostCommitment
from app.models.cost_element import CostElement
from app.schemas.cost_commitment import CostCommitmentCreate, CostCommitmentUpdate
from app.services.cost_element import _require_live_period


async def _get_parent_element(db: AsyncSession, cost_element_id: uuid.UUID) -> CostElement:
    element = await db.get(CostElement, cost_element_id)
    if element is None:
        raise HTTPException(status_code=404, detail="Cost element not found")
    return element


async def list_commitments(db: AsyncSession, cost_element_id: uuid.UUID) -> list[CostCommitment]:
    result = await db.execute(
        select(CostCommitment)
        .where(CostCommitment.cost_element_id == cost_element_id)
        .order_by(CostCommitment.created_at)
    )
    return list(result.scalars().all())


async def get_commitment(db: AsyncSession, commitment_id: uuid.UUID) -> CostCommitment:
    commitment = await db.get(CostCommitment, commitment_id)
    if commitment is None:
        raise HTTPException(status_code=404, detail="Commitment not found")
    return commitment


async def create_commitment(db: AsyncSession, data: CostCommitmentCreate) -> CostCommitment:
    element = await _get_parent_element(db, data.cost_element_id)
    await _require_live_period(db, element.period_id)
    commitment = CostCommitment(**data.model_dump())
    db.add(commitment)
    await db.commit()
    await db.refresh(commitment)
    return commitment


async def update_commitment(
    db: AsyncSession, commitment_id: uuid.UUID, data: CostCommitmentUpdate
) -> CostCommitment:
    commitment = await get_commitment(db, commitment_id)
    element = await _get_parent_element(db, commitment.cost_element_id)
    await _require_live_period(db, element.period_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(commitment, field, value)
    await db.commit()
    await db.refresh(commitment)
    return commitment


async def delete_commitment(db: AsyncSession, commitment_id: uuid.UUID) -> None:
    commitment = await get_commitment(db, commitment_id)
    element = await _get_parent_element(db, commitment.cost_element_id)
    await _require_live_period(db, element.period_id)
    await db.delete(commitment)
    await db.commit()
