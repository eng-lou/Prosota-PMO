from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_db_user
from app.database import get_db
from app.schemas.icd_comment import IcdCommentCreate, IcdCommentResponse, IcdCommentUpdate
from app.services import icd_comment as svc

router = APIRouter(prefix="/icd-comments", tags=["icd-comments"])


@router.get("/", response_model=list[IcdCommentResponse])
async def list_comments(
    icd_item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list:
    return await svc.list_comments(db, icd_item_id)


@router.post("/", response_model=IcdCommentResponse, status_code=201)
async def create_comment(
    data: IcdCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_db_user),
):
    return await svc.create_comment(db, data, current_user)


@router.patch("/{comment_id}", response_model=IcdCommentResponse)
async def update_comment(
    comment_id: uuid.UUID,
    data: IcdCommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_db_user),
):
    return await svc.update_comment(db, comment_id, data, current_user)


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_db_user),
) -> Response:
    await svc.delete_comment(db, comment_id, current_user)
    return Response(status_code=204)
