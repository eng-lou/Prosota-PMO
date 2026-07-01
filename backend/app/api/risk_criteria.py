from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.risk_criteria import (
    RiskImpactCriterionResponse,
    RiskImpactCriterionUpdate,
    RiskProbabilityCriterionResponse,
    RiskProbabilityCriterionUpdate,
)
from app.services import risk_criteria as svc

router = APIRouter(prefix="/risk-criteria", tags=["risk-criteria"])


@router.get("/probability", response_model=list[RiskProbabilityCriterionResponse])
async def list_probability_criteria(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_probability_criteria(db, project_id)


@router.patch("/probability/{criterion_id}", response_model=RiskProbabilityCriterionResponse)
async def update_probability_criterion(
    criterion_id: uuid.UUID,
    data: RiskProbabilityCriterionUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_probability_criterion(db, criterion_id, data)


@router.get("/impact", response_model=list[RiskImpactCriterionResponse])
async def list_impact_criteria(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_impact_criteria(db, project_id)


@router.patch("/impact/{criterion_id}", response_model=RiskImpactCriterionResponse)
async def update_impact_criterion(
    criterion_id: uuid.UUID,
    data: RiskImpactCriterionUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_impact_criterion(db, criterion_id, data)
