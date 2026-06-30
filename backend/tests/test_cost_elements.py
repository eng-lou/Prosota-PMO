from __future__ import annotations

import uuid
from decimal import Decimal

from httpx import AsyncClient

from app.models.period import Period
from app.models.project import Project


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _create(client: AsyncClient, project: Project, period: Period, **kwargs) -> dict:
    resp = await client.post("/api/v1/cost-elements/", json={
        "project_id": str(project.id),
        "period_id": str(period.id),
        **kwargs,
    })
    assert resp.status_code == 201, resp.json()
    return resp.json()


# ---------------------------------------------------------------------------
# Fixed elements — standard CRUD
# ---------------------------------------------------------------------------

async def test_create_fixed_element(client: AsyncClient, project: Project, live_period: Period):
    el = await _create(client, project, live_period,
        description="Substructure",
        element_group="Structure",
        budget="500000.00",
        forecast="520000.00",
        actuals="250000.00",
    )
    assert el["element_type"] == "fixed"
    assert el["rate"] is None
    assert float(el["budget"]) == 500000.00
    assert el["computed_budget"] is None  # fixed elements have no computed value


async def test_list_cost_elements_by_project(client: AsyncClient, project: Project, live_period: Period):
    for desc in ["Substructure", "Superstructure", "Envelope"]:
        await _create(client, project, live_period, description=desc, budget="100000.00")

    resp = await client.get("/api/v1/cost-elements/", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    assert len(resp.json()) == 3


async def test_get_cost_element(client: AsyncClient, project: Project, live_period: Period):
    el = await _create(client, project, live_period, description="MEP", budget="200000.00")
    resp = await client.get(f"/api/v1/cost-elements/{el['id']}")
    assert resp.status_code == 200
    assert resp.json()["description"] == "MEP"


async def test_get_cost_element_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/cost-elements/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_update_cost_element(client: AsyncClient, project: Project, live_period: Period):
    el = await _create(client, project, live_period, description="FF&E", budget="80000.00")
    resp = await client.patch(f"/api/v1/cost-elements/{el['id']}", json={
        "budget": "90000.00",
        "forecast": "88000.00",
    })
    assert resp.status_code == 200
    assert float(resp.json()["budget"]) == 90000.00
    assert float(resp.json()["forecast"]) == 88000.00
    assert resp.json()["description"] == "FF&E"  # unchanged


async def test_delete_cost_element(client: AsyncClient, project: Project, live_period: Period):
    el = await _create(client, project, live_period, description="External works")
    resp = await client.delete(f"/api/v1/cost-elements/{el['id']}")
    assert resp.status_code == 204
    assert (await client.get(f"/api/v1/cost-elements/{el['id']}")).status_code == 404


# ---------------------------------------------------------------------------
# Percentage elements — core mechanic
# ---------------------------------------------------------------------------

async def test_percentage_element_computed_from_fixed_subtotal(
    client: AsyncClient, project: Project, live_period: Period
):
    """Prelims at 15% should compute against the live sum of fixed element budgets."""
    await _create(client, project, live_period, description="Substructure", budget="400000.00", forecast="420000.00", actuals="200000.00")
    await _create(client, project, live_period, description="Superstructure", budget="600000.00", forecast="610000.00", actuals="300000.00")
    # Fixed subtotals: budget=1,000,000 | forecast=1,030,000 | actuals=500,000

    prelims = await _create(client, project, live_period,
        description="Prelims",
        element_type="percentage",
        rate="0.15",  # 15%
    )
    assert prelims["element_type"] == "percentage"
    assert prelims["budget"] is None           # not stored
    assert float(prelims["computed_budget"]) == 150000.00    # 15% of 1,000,000
    assert float(prelims["computed_forecast"]) == 154500.00  # 15% of 1,030,000
    assert float(prelims["computed_actuals"]) == 75000.00    # 15% of 500,000


async def test_percentage_computed_value_updates_when_fixed_changes(
    client: AsyncClient, project: Project, live_period: Period
):
    """Computed value must reflect the current fixed subtotal, not a stored snapshot."""
    fixed = await _create(client, project, live_period, description="Works", budget="1000000.00")
    contingency = await _create(client, project, live_period,
        description="Construction Contingency",
        element_type="percentage",
        rate="0.04",  # 4%
    )
    assert float(contingency["computed_budget"]) == 40000.00  # 4% of 1,000,000

    # Update the fixed element budget
    await client.patch(f"/api/v1/cost-elements/{fixed['id']}", json={"budget": "2000000.00"})

    # Re-fetch the percentage element — computed value must have updated
    updated = (await client.get(f"/api/v1/cost-elements/{contingency['id']}")).json()
    assert float(updated["computed_budget"]) == 80000.00  # 4% of 2,000,000


async def test_multiple_percentage_elements_each_use_same_fixed_subtotal(
    client: AsyncClient, project: Project, live_period: Period
):
    """All on-costs apply to the same fixed subtotal, not to each other."""
    await _create(client, project, live_period, description="Base works", budget="1000000.00")

    on_costs = [
        ("Prelims", "0.15"),
        ("Construction Contingency", "0.04"),
        ("Design Contingency", "0.02"),
        ("OH&P", "0.056"),
        ("Insurance", "0.013"),
    ]
    results = {}
    for desc, rate in on_costs:
        el = await _create(client, project, live_period, description=desc, element_type="percentage", rate=rate)
        results[desc] = float(el["computed_budget"])

    assert results["Prelims"] == 150000.00
    assert results["Construction Contingency"] == 40000.00
    assert results["Design Contingency"] == 20000.00
    assert results["OH&P"] == 56000.00
    assert results["Insurance"] == 13000.00


async def test_list_includes_computed_values_for_percentage_elements(
    client: AsyncClient, project: Project, live_period: Period
):
    """List endpoint must return computed values, not nulls, for percentage elements."""
    await _create(client, project, live_period, description="Works", budget="500000.00")
    await _create(client, project, live_period, description="Prelims", element_type="percentage", rate="0.15")

    elements = (await client.get("/api/v1/cost-elements/", params={"project_id": str(project.id)})).json()
    pct = next(e for e in elements if e["element_type"] == "percentage")
    assert float(pct["computed_budget"]) == 75000.00  # 15% of 500,000


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

async def test_percentage_element_requires_rate(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/cost-elements/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "description": "Bad percentage",
        "element_type": "percentage",
        # rate intentionally omitted
    })
    assert resp.status_code == 422


async def test_fixed_element_rejects_rate(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/cost-elements/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "description": "Fixed with rate",
        "element_type": "fixed",
        "rate": "0.15",
    })
    assert resp.status_code == 422


async def test_create_rejects_frozen_period(client: AsyncClient, project: Project, frozen_period: Period):
    resp = await client.post("/api/v1/cost-elements/", json={
        "project_id": str(project.id),
        "period_id": str(frozen_period.id),
        "description": "Should be rejected",
    })
    assert resp.status_code == 422
