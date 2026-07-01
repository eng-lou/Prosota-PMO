from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.icd_criteria import IcdCriterion
from app.schemas.icd_criteria import Dimension, IcdCriterionUpdate

# Defaults per dimension, ascending level (1 = lowest). Narrative wording follows
# Rita Mulcahy's issue urgency/impact assessment guidance so "High priority" or
# "Critical severity" means the same thing to everyone rating an item.
_DEFAULT_CRITERIA: dict[Dimension, list[tuple[int, str, str]]] = {
    "priority": [
        (1, "Low", "No immediate action needed; monitor and address in the normal course of business."),
        (2, "Medium", "Address within the current reporting period; moderate consequence if delayed."),
        (3, "High", "Requires prompt attention; meaningful cost/schedule/quality consequence if not addressed soon."),
        (4, "Critical", "Immediate escalation required; project-threatening if not resolved without delay."),
    ],
    "severity": [
        (1, "Low", "Minor inconvenience; workaround available; negligible impact on cost, schedule, or quality."),
        (2, "Medium", "Noticeable impact; manageable within existing contingency or float."),
        (3, "High", "Significant impact on cost, schedule, or quality; requires management action."),
        (4, "Critical", "Severe impact; threatens project objectives; requires immediate senior management involvement."),
    ],
    "quality_impact": [
        (1, "None", "No effect on specification, workmanship, or performance requirements."),
        (2, "Low", "Minor deviation from specification; within acceptable tolerance."),
        (3, "Medium", "Noticeable deviation; may require design or QA sign-off."),
        (4, "High", "Significant deviation from specification or performance requirements; may affect fitness for purpose."),
    ],
}


async def list_criteria(db: AsyncSession, project_id: uuid.UUID, dimension: Dimension) -> list[IcdCriterion]:
    result = await db.execute(
        select(IcdCriterion)
        .where(IcdCriterion.project_id == project_id, IcdCriterion.dimension == dimension)
        .order_by(IcdCriterion.level)
    )
    criteria = list(result.scalars().all())
    if criteria:
        return criteria

    criteria = [
        IcdCriterion(project_id=project_id, dimension=dimension, level=level, label=label, description=desc)
        for level, label, desc in _DEFAULT_CRITERIA[dimension]
    ]
    db.add_all(criteria)
    await db.commit()
    for c in criteria:
        await db.refresh(c)
    return criteria


async def update_criterion(
    db: AsyncSession, criterion_id: uuid.UUID, data: IcdCriterionUpdate
) -> IcdCriterion:
    criterion = await db.get(IcdCriterion, criterion_id)
    if criterion is None:
        raise HTTPException(status_code=404, detail="Criterion not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(criterion, field, value)
    await db.commit()
    await db.refresh(criterion)
    return criterion
