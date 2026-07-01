from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.risk_reassessment import (
    RiskReassessmentCreate,
    RiskReassessmentResponse,
    RiskReassessmentUpdate,
)
from app.services import risk_reassessment as svc

router = APIRouter(prefix="/risk-reassessments", tags=["risk-reassessments"])


@router.get("/", response_model=list[RiskReassessmentResponse])
async def list_reassessments(
    risk_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_reassessments(db, risk_id)


@router.post("/", response_model=RiskReassessmentResponse, status_code=201)
async def create_reassessment(
    data: RiskReassessmentCreate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_reassessment(db, data)


@router.patch("/{reassessment_id}", response_model=RiskReassessmentResponse)
async def update_reassessment(
    reassessment_id: uuid.UUID,
    data: RiskReassessmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_reassessment(db, reassessment_id, data)


@router.delete("/{reassessment_id}", status_code=204)
async def delete_reassessment(
    reassessment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    await svc.delete_reassessment(db, reassessment_id)
    return Response(status_code=204)
