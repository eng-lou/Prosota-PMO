from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.risk_criteria import RiskImpactCriterion, RiskProbabilityCriterion
from app.schemas.risk_criteria import (
    RiskImpactCriterionUpdate,
    RiskProbabilityCriterionUpdate,
)

# Defaults match the prototype's Criteria & Thresholds tab exactly, so a project
# starts with sensible, standard bands that can then be edited per-project.
_DEFAULT_PROBABILITY_CRITERIA = [
    (1, "Very Low", "0.00", "0.05", "Unlikely to occur"),
    (2, "Low", "0.05", "0.25", "May occur occasionally"),
    (3, "Medium", "0.25", "0.50", "Likely to occur at some point"),
    (4, "High", "0.50", "0.75", "More likely than not"),
    (5, "Very High", "0.75", "1.00", "Almost certain to occur"),
]

_DEFAULT_IMPACT_CRITERIA = [
    (1, "Negligible", None, 50_000, None, 7),
    (2, "Low", 50_000, 200_000, 7, 14),
    (3, "Moderate", 200_000, 500_000, 14, 28),
    (4, "High", 500_000, 1_000_000, 28, 56),
    (5, "Critical", 1_000_000, None, 56, None),
]


async def list_probability_criteria(
    db: AsyncSession, project_id: uuid.UUID
) -> list[RiskProbabilityCriterion]:
    result = await db.execute(
        select(RiskProbabilityCriterion)
        .where(RiskProbabilityCriterion.project_id == project_id)
        .order_by(RiskProbabilityCriterion.level)
    )
    criteria = list(result.scalars().all())
    if criteria:
        return criteria

    criteria = [
        RiskProbabilityCriterion(
            project_id=project_id, level=level, label=label,
            min_probability=min_p, max_probability=max_p, description=desc,
        )
        for level, label, min_p, max_p, desc in _DEFAULT_PROBABILITY_CRITERIA
    ]
    db.add_all(criteria)
    await db.commit()
    for c in criteria:
        await db.refresh(c)
    return criteria


async def list_impact_criteria(db: AsyncSession, project_id: uuid.UUID) -> list[RiskImpactCriterion]:
    result = await db.execute(
        select(RiskImpactCriterion)
        .where(RiskImpactCriterion.project_id == project_id)
        .order_by(RiskImpactCriterion.level)
    )
    criteria = list(result.scalars().all())
    if criteria:
        return criteria

    criteria = [
        RiskImpactCriterion(
            project_id=project_id, level=level, label=label,
            min_cost=min_c, max_cost=max_c,
            min_schedule_days=min_d, max_schedule_days=max_d,
        )
        for level, label, min_c, max_c, min_d, max_d in _DEFAULT_IMPACT_CRITERIA
    ]
    db.add_all(criteria)
    await db.commit()
    for c in criteria:
        await db.refresh(c)
    return criteria


async def update_probability_criterion(
    db: AsyncSession, criterion_id: uuid.UUID, data: RiskProbabilityCriterionUpdate
) -> RiskProbabilityCriterion:
    criterion = await db.get(RiskProbabilityCriterion, criterion_id)
    if criterion is None:
        raise HTTPException(status_code=404, detail="Probability criterion not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(criterion, field, value)
    await db.commit()
    await db.refresh(criterion)
    return criterion


async def update_impact_criterion(
    db: AsyncSession, criterion_id: uuid.UUID, data: RiskImpactCriterionUpdate
) -> RiskImpactCriterion:
    criterion = await db.get(RiskImpactCriterion, criterion_id)
    if criterion is None:
        raise HTTPException(status_code=404, detail="Impact criterion not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(criterion, field, value)
    await db.commit()
    await db.refresh(criterion)
    return criterion
