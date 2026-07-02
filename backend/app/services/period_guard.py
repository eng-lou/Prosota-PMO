from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import Period


async def require_live_period(db: AsyncSession, period_id: uuid.UUID) -> None:
    """Shared period-freeze check, used by the generalised Reassessment service.
    Risk/ICD/Cost each still keep their own identical private copy for their
    own writes — left untouched here to avoid disturbing already-passing
    tests; this shared version is for new cross-module code only."""
    period = await db.get(Period, period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")
    if period.freeze_status != "live":
        raise HTTPException(
            status_code=422,
            detail=f"Period '{period.period_label}' is {period.freeze_status}. Writes to frozen periods are not allowed.",
        )
