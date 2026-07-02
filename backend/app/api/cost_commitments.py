from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.cost_commitment import CostCommitmentCreate, CostCommitmentResponse, CostCommitmentUpdate
from app.services import cost_commitment as svc

router = APIRouter(prefix="/cost-commitments", tags=["cost-commitments"])


@router.get("/", response_model=list[CostCommitmentResponse])
async def list_commitments(
    cost_element_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_commitments(db, cost_element_id)


@router.post("/", response_model=CostCommitmentResponse, status_code=201)
async def create_commitment(
    data: CostCommitmentCreate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_commitment(db, data)


@router.patch("/{commitment_id}", response_model=CostCommitmentResponse)
async def update_commitment(
    commitment_id: uuid.UUID,
    data: CostCommitmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_commitment(db, commitment_id, data)


@router.delete("/{commitment_id}", status_code=204)
async def delete_commitment(
    commitment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    await svc.delete_commitment(db, commitment_id)
    return Response(status_code=204)
