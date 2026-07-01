from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.icd_criteria import Dimension, IcdCriterionResponse, IcdCriterionUpdate
from app.services import icd_criteria as svc

router = APIRouter(prefix="/icd-criteria", tags=["icd-criteria"])


@router.get("/{dimension}", response_model=list[IcdCriterionResponse])
async def list_criteria(
    dimension: Dimension,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_criteria(db, project_id, dimension)


@router.patch("/criterion/{criterion_id}", response_model=IcdCriterionResponse)
async def update_criterion(
    criterion_id: uuid.UUID,
    data: IcdCriterionUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_criterion(db, criterion_id, data)
