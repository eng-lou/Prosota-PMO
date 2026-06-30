from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_db_user
from app.database import get_db
from app.models.period import Period
from app.models.project import Project
from app.schemas.period import PeriodCreate, PeriodResponse, PeriodUpdate

router = APIRouter(prefix="/periods", tags=["periods"])


async def _get_period_checked(
    period_id: uuid.UUID,
    db: AsyncSession,
    current_user,
) -> Period:
    period = await db.get(Period, period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")
    project = await db.get(Project, period.project_id)
    if project is None or project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Period not found")
    return period


@router.get("/", response_model=list[PeriodResponse])
async def list_periods(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_db_user),
) -> list:
    project = await db.get(Project, project_id)
    if project is None or project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Project not found")
    result = await db.execute(
        select(Period).where(Period.project_id == project_id)
    )
    return list(result.scalars().all())


@router.post("/", response_model=PeriodResponse, status_code=201)
async def create_period(
    data: PeriodCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_db_user),
):
    project = await db.get(Project, data.project_id)
    if project is None or project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Project not found")
    period = Period(**data.model_dump())
    db.add(period)
    await db.commit()
    await db.refresh(period)
    return period


@router.get("/{period_id}", response_model=PeriodResponse)
async def get_period(
    period_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_db_user),
):
    return await _get_period_checked(period_id, db, current_user)


@router.patch("/{period_id}", response_model=PeriodResponse)
async def update_period(
    period_id: uuid.UUID,
    data: PeriodUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_db_user),
):
    period = await _get_period_checked(period_id, db, current_user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(period, field, value)
    await db.commit()
    await db.refresh(period)
    return period


@router.delete("/{period_id}", status_code=204)
async def delete_period(
    period_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_db_user),
) -> Response:
    period = await _get_period_checked(period_id, db, current_user)
    await db.delete(period)
    await db.commit()
    return Response(status_code=204)
