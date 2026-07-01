from __future__ import annotations

import uuid

from sqlalchemy import ColumnElement, Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base


async def next_code(
    db: AsyncSession,
    model: type[Base],
    prefix: str,
    project_id: uuid.UUID,
    extra_filter: ColumnElement[bool] | None = None,
) -> str:
    """Generate the next sequential human-readable code for a record type, scoped to a
    project (and, for discriminated tables like icd_items, a sub-type via extra_filter).

    Codes are never reused, even after deletes — the next number is always
    max(existing) + 1, not count(existing) + 1.
    """
    stmt = select(func.max(cast(func.split_part(model.code, "-", 2), Integer))).where(
        model.project_id == project_id
    )
    if extra_filter is not None:
        stmt = stmt.where(extra_filter)
    current_max = (await db.execute(stmt)).scalar()
    next_seq = (current_max or 0) + 1
    return f"{prefix}-{next_seq:04d}"
