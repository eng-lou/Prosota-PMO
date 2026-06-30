from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.icd_item import IcdItemCreate, IcdItemResponse, IcdItemUpdate
from app.services import icd_item as svc

router = APIRouter(prefix="/icd-items", tags=["icd-items"])


@router.get("/", response_model=list[IcdItemResponse])
async def list_icd_items(
    project_id: uuid.UUID,
    period_id: uuid.UUID | None = None,
    item_type: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_icd_items(db, project_id, period_id, item_type)


@router.post("/", response_model=IcdItemResponse, status_code=201)
async def create_icd_item(
    data: IcdItemCreate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_icd_item(db, data)


@router.get("/{item_id}", response_model=IcdItemResponse)
async def get_icd_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_icd_item(db, item_id)


@router.patch("/{item_id}", response_model=IcdItemResponse)
async def update_icd_item(
    item_id: uuid.UUID,
    data: IcdItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.update_icd_item(db, item_id, data)


@router.delete("/{item_id}", status_code=204)
async def delete_icd_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    await svc.delete_icd_item(db, item_id)
    return Response(status_code=204)
