from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.record_link import RecordLinkCreate, RecordLinkResponse
from app.services import record_link as svc

router = APIRouter(prefix="/record-links", tags=["record-links"])


@router.get("/", response_model=list[RecordLinkResponse])
async def list_links(
    record_type: str,
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_links(db, record_type, record_id)


@router.post("/", response_model=RecordLinkResponse, status_code=201)
async def create_link(
    data: RecordLinkCreate,
    db: AsyncSession = Depends(get_db),
):
    return await svc.create_link(db, data)


@router.get("/{link_id}", response_model=RecordLinkResponse)
async def get_link(
    link_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_link(db, link_id)


@router.delete("/{link_id}", status_code=204)
async def delete_link(
    link_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    await svc.delete_link(db, link_id)
    return Response(status_code=204)
