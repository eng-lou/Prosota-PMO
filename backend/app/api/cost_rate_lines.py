from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.cost_rate_line import CostRateLineCreate, CostRateLineResponse, CostRateLineUpdate
from app.services import cost_rate_line as svc

router = APIRouter(prefix="/cost-rate-lines", tags=["cost-rate-lines"])


@router.get("/", response_model=list[CostRateLineResponse])
async def list_rate_lines(
    cost_element_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_rate_lines(db, cost_element_id)


@router.post("/", response_model=CostRateLineResponse, status_code=201)
async def create_rate_line(
    data: CostRateLineCreate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_rate_line(db, data)


@router.patch("/{line_id}", response_model=CostRateLineResponse)
async def update_rate_line(
    line_id: uuid.UUID,
    data: CostRateLineUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_rate_line(db, line_id, data)


@router.delete("/{line_id}", status_code=204)
async def delete_rate_line(
    line_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    await svc.delete_rate_line(db, line_id)
    return Response(status_code=204)
