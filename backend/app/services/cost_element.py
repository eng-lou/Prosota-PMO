from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cost_element import CostElement
from app.models.period import Period
from app.schemas.cost_element import CostElementCreate, CostElementResponse, CostElementUpdate
from app.services.reference_codes import next_code


async def _require_live_period(db: AsyncSession, period_id: uuid.UUID) -> None:
    period = await db.get(Period, period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")
    if period.freeze_status != "live":
        raise HTTPException(
            status_code=422,
            detail=f"Period '{period.period_label}' is {period.freeze_status}. Writes to frozen periods are not allowed.",
        )


async def _fixed_subtotals(
    db: AsyncSession, project_id: uuid.UUID, period_id: uuid.UUID
) -> tuple[Decimal, Decimal, Decimal]:
    """Return (sum_budget, sum_forecast, sum_actuals) for all fixed elements in this project/period."""
    q = select(
        func.coalesce(func.sum(CostElement.budget), 0).label("budget"),
        func.coalesce(func.sum(CostElement.forecast), 0).label("forecast"),
        func.coalesce(func.sum(CostElement.actuals), 0).label("actuals"),
    ).where(
        CostElement.project_id == project_id,
        CostElement.period_id == period_id,
        CostElement.element_type == "fixed",
    )
    row = (await db.execute(q)).one()
    return Decimal(str(row.budget)), Decimal(str(row.forecast)), Decimal(str(row.actuals))


def _apply_computed(element: CostElement, sub_budget: Decimal, sub_forecast: Decimal, sub_actuals: Decimal) -> CostElementResponse:
    data = CostElementResponse.model_validate(element)
    if element.element_type == "percentage" and element.rate is not None:
        rate = Decimal(str(element.rate))
        data.computed_budget = (rate * sub_budget).quantize(Decimal("0.01"))
        data.computed_forecast = (rate * sub_forecast).quantize(Decimal("0.01"))
        data.computed_actuals = (rate * sub_actuals).quantize(Decimal("0.01"))
    return data


async def list_cost_elements(
    db: AsyncSession,
    project_id: uuid.UUID,
    period_id: uuid.UUID | None = None,
) -> list[CostElementResponse]:
    q = select(CostElement).where(CostElement.project_id == project_id)
    if period_id is not None:
        q = q.where(CostElement.period_id == period_id)
    elements = list((await db.execute(q)).scalars().all())

    # Group percentage calculations by period to avoid N+1 subtotal queries
    period_subtotals: dict[uuid.UUID, tuple[Decimal, Decimal, Decimal]] = {}
    for el in elements:
        if el.element_type == "percentage" and el.period_id not in period_subtotals:
            period_subtotals[el.period_id] = await _fixed_subtotals(db, project_id, el.period_id)

    results = []
    for el in elements:
        if el.element_type == "percentage":
            subs = period_subtotals[el.period_id]
            results.append(_apply_computed(el, *subs))
        else:
            results.append(CostElementResponse.model_validate(el))
    return results


async def get_cost_element(db: AsyncSession, element_id: uuid.UUID) -> CostElementResponse:
    el = await db.get(CostElement, element_id)
    if el is None:
        raise HTTPException(status_code=404, detail="Cost element not found")
    if el.element_type == "percentage":
        subs = await _fixed_subtotals(db, el.project_id, el.period_id)
        return _apply_computed(el, *subs)
    return CostElementResponse.model_validate(el)


async def create_cost_element(db: AsyncSession, data: CostElementCreate) -> CostElementResponse:
    await _require_live_period(db, data.period_id)
    code = await next_code(db, CostElement, "CST", data.project_id)
    el = CostElement(**data.model_dump(), code=code)
    db.add(el)
    await db.commit()
    await db.refresh(el)
    return await get_cost_element(db, el.id)


async def update_cost_element(
    db: AsyncSession, element_id: uuid.UUID, data: CostElementUpdate
) -> CostElementResponse:
    el = await db.get(CostElement, element_id)
    if el is None:
        raise HTTPException(status_code=404, detail="Cost element not found")
    await _require_live_period(db, el.period_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(el, field, value)
    await db.commit()
    await db.refresh(el)
    return await get_cost_element(db, el.id)


async def delete_cost_element(db: AsyncSession, element_id: uuid.UUID) -> None:
    el = await db.get(CostElement, element_id)
    if el is None:
        raise HTTPException(status_code=404, detail="Cost element not found")
    await _require_live_period(db, el.period_id)
    await db.delete(el)
    await db.commit()
