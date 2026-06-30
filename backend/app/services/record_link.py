from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import or_, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.record_link import RecordLink
from app.schemas.record_link import RecordLinkCreate


async def list_links(
    db: AsyncSession,
    record_type: str,
    record_id: uuid.UUID,
) -> list[RecordLink]:
    """Return all links where record_id appears as either source or target."""
    q = select(RecordLink).where(
        or_(
            and_(RecordLink.source_type == record_type, RecordLink.source_id == record_id),
            and_(RecordLink.target_type == record_type, RecordLink.target_id == record_id),
        )
    )
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_link(db: AsyncSession, link_id: uuid.UUID) -> RecordLink:
    link = await db.get(RecordLink, link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Record link not found")
    return link


async def create_link(db: AsyncSession, data: RecordLinkCreate) -> RecordLink:
    if data.source_id == data.target_id and data.source_type == data.target_type:
        raise HTTPException(status_code=422, detail="A record cannot be linked to itself")
    link = RecordLink(**data.model_dump())
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def delete_link(db: AsyncSession, link_id: uuid.UUID) -> None:
    link = await get_link(db, link_id)
    await db.delete(link)
    await db.commit()
