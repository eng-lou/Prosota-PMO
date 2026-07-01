from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.icd_reassessment import (
    IcdReassessmentCreate,
    IcdReassessmentResponse,
    IcdReassessmentUpdate,
)
from app.services import icd_reassessment as svc

router = APIRouter(prefix="/icd-reassessments", tags=["icd-reassessments"])


@router.get("/", response_model=list[IcdReassessmentResponse])
async def list_reassessments(
    icd_item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_reassessments(db, icd_item_id)


@router.post("/", response_model=IcdReassessmentResponse, status_code=201)
async def create_reassessment(
    data: IcdReassessmentCreate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_reassessment(db, data)


@router.patch("/{reassessment_id}", response_model=IcdReassessmentResponse)
async def update_reassessment(
    reassessment_id: uuid.UUID,
    data: IcdReassessmentUpdate,
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
