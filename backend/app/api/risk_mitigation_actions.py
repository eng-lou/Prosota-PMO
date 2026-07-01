from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.risk_mitigation_action import (
    RiskMitigationActionCreate,
    RiskMitigationActionResponse,
    RiskMitigationActionUpdate,
)
from app.services import risk_mitigation_action as svc

router = APIRouter(prefix="/risk-mitigation-actions", tags=["risk-mitigation-actions"])


@router.get("/", response_model=list[RiskMitigationActionResponse])
async def list_actions(
    risk_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_actions(db, risk_id)


@router.post("/", response_model=RiskMitigationActionResponse, status_code=201)
async def create_action(
    data: RiskMitigationActionCreate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_action(db, data)


@router.get("/{action_id}", response_model=RiskMitigationActionResponse)
async def get_action(
    action_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_action(db, action_id)


@router.patch("/{action_id}", response_model=RiskMitigationActionResponse)
async def update_action(
    action_id: uuid.UUID,
    data: RiskMitigationActionUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_action(db, action_id, data)


@router.delete("/{action_id}", status_code=204)
async def delete_action(
    action_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    await svc.delete_action(db, action_id)
    return Response(status_code=204)
