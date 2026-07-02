from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.cost_variance_criterion import (
    CostVarianceCriterionResponse,
    CostVarianceCriterionUpdate,
)
from app.services import cost_variance_criterion as svc

router = APIRouter(prefix="/cost-variance-criteria", tags=["cost-variance-criteria"])


@router.get("/", response_model=list[CostVarianceCriterionResponse])
async def list_criteria(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_criteria(db, project_id)


@router.patch("/{criterion_id}", response_model=CostVarianceCriterionResponse)
async def update_criterion(
    criterion_id: uuid.UUID,
    data: CostVarianceCriterionUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_criterion(db, criterion_id, data)
