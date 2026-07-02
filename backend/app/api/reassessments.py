from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.reassessment import RecordType, ReassessmentCreate, ReassessmentResponse, ReassessmentUpdate
from app.services import reassessment as svc

router = APIRouter(prefix="/reassessments", tags=["reassessments"])


@router.get("/", response_model=list[ReassessmentResponse])
async def list_reassessments(
    record_type: RecordType,
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_reassessments(db, record_type, record_id)


@router.post("/", response_model=ReassessmentResponse, status_code=201)
async def create_reassessment(
    data: ReassessmentCreate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_reassessment(db, data)


@router.patch("/{reassessment_id}", response_model=ReassessmentResponse)
async def update_reassessment(
    reassessment_id: uuid.UUID,
    data: ReassessmentUpdate,
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
