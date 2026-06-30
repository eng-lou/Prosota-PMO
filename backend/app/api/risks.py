from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.risk import RiskCreate, RiskResponse, RiskUpdate
from app.services import risk as svc

router = APIRouter(prefix="/risks", tags=["risks"])


@router.get("/", response_model=list[RiskResponse])
async def list_risks(
    project_id: uuid.UUID,
    period_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_risks(db, project_id, period_id)


@router.post("/", response_model=RiskResponse, status_code=201)
async def create_risk(
    data: RiskCreate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_risk(db, data)


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(
    risk_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_risk(db, risk_id)


@router.patch("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: uuid.UUID,
    data: RiskUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_risk(db, risk_id, data)


@router.delete("/{risk_id}", status_code=204)
async def delete_risk(
    risk_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    await svc.delete_risk(db, risk_id)
    return Response(status_code=204)
