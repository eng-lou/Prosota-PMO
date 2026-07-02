from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cost_variance_criterion import CostVarianceCriterion
from app.schemas.cost_variance_criterion import CostVarianceCriterionUpdate

# Defaults: variance % = (forecast - budget) / budget * 100 — forecast (EAC) vs
# budget, not vs the frozen Rev A baseline (which only moves on a deliberate
# re-baseline and wouldn't stay consistent with the Cost Summary's Budget vs
# Forecast comparison otherwise).
_DEFAULT_CRITERIA = [
    (1, "Saving", None, "-1.00", "Forecast more than 1% under budget"),
    (2, "On Budget", "-1.00", "1.00", "Forecast within 1% of budget"),
    (3, "Monitor", "1.00", "5.00", "Forecast 1-5% over budget — keep an eye on it"),
    (4, "Over Budget", "5.00", None, "Forecast more than 5% over budget"),
]


async def list_criteria(db: AsyncSession, project_id: uuid.UUID) -> list[CostVarianceCriterion]:
    result = await db.execute(
        select(CostVarianceCriterion)
        .where(CostVarianceCriterion.project_id == project_id)
        .order_by(CostVarianceCriterion.level)
    )
    criteria = list(result.scalars().all())
    if criteria:
        return criteria

    criteria = [
        CostVarianceCriterion(project_id=project_id, level=level, label=label, min_pct=min_p, max_pct=max_p, description=desc)
        for level, label, min_p, max_p, desc in _DEFAULT_CRITERIA
    ]
    db.add_all(criteria)
    await db.commit()
    for c in criteria:
        await db.refresh(c)
    return criteria


async def update_criterion(
    db: AsyncSession, criterion_id: uuid.UUID, data: CostVarianceCriterionUpdate
) -> CostVarianceCriterion:
    criterion = await db.get(CostVarianceCriterion, criterion_id)
    if criterion is None:
        raise HTTPException(status_code=404, detail="Criterion not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(criterion, field, value)
    await db.commit()
    await db.refresh(criterion)
    return criterion
