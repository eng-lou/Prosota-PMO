from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.icd_comment import IcdComment
from app.models.icd_item import IcdItem
from app.models.user import User
from app.schemas.icd_comment import IcdCommentCreate, IcdCommentUpdate
from app.services.icd_item import _require_live_period


async def list_comments(db: AsyncSession, icd_item_id: uuid.UUID) -> list[IcdComment]:
    result = await db.execute(
        select(IcdComment)
        .where(IcdComment.icd_item_id == icd_item_id)
        .order_by(IcdComment.created_at)
    )
    return list(result.scalars().all())


async def get_comment(db: AsyncSession, comment_id: uuid.UUID) -> IcdComment:
    comment = await db.get(IcdComment, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


async def create_comment(
    db: AsyncSession, data: IcdCommentCreate, current_user: User
) -> IcdComment:
    item = await db.get(IcdItem, data.icd_item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="ICD item not found")
    await _require_live_period(db, item.period_id)

    comment = IcdComment(
        icd_item_id=data.icd_item_id,
        author_id=current_user.id,
        author_name=current_user.display_name,
        body=data.body,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def update_comment(
    db: AsyncSession, comment_id: uuid.UUID, data: IcdCommentUpdate, current_user: User
) -> IcdComment:
    comment = await get_comment(db, comment_id)
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the comment's author can edit it")
    item = await db.get(IcdItem, comment.icd_item_id)
    if item is not None:
        await _require_live_period(db, item.period_id)
    comment.body = data.body
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(db: AsyncSession, comment_id: uuid.UUID, current_user: User) -> None:
    comment = await get_comment(db, comment_id)
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the comment's author can delete it")
    item = await db.get(IcdItem, comment.icd_item_id)
    if item is not None:
        await _require_live_period(db, item.period_id)
    await db.delete(comment)
    await db.commit()
