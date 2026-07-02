from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import Period
from app.models.project import Project


async def _create_element(client: AsyncClient, project: Project, period: Period, description: str = "Piling") -> dict:
    resp = await client.post("/api/v1/cost-elements/", json={
        "project_id": str(project.id), "period_id": str(period.id), "description": description,
    })
    assert resp.status_code == 201, resp.json()
    return resp.json()


async def test_create_commitment(client: AsyncClient, project: Project, live_period: Period):
    el = await _create_element(client, project, live_period)
    resp = await client.post("/api/v1/cost-commitments/", json={
        "cost_element_id": el["id"], "po_reference": "PO-PIL-001", "description": "Huber piling", "amount": "118000.00",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["po_reference"] == "PO-PIL-001"
    assert float(data["amount"]) == 118000.00


async def test_list_commitments_oldest_first(client: AsyncClient, project: Project, live_period: Period):
    el = await _create_element(client, project, live_period)
    await client.post("/api/v1/cost-commitments/", json={"cost_element_id": el["id"], "description": "First PO", "amount": "1000.00"})
    await client.post("/api/v1/cost-commitments/", json={"cost_element_id": el["id"], "description": "Second PO", "amount": "2000.00"})

    resp = await client.get("/api/v1/cost-commitments/", params={"cost_element_id": el["id"]})
    assert resp.status_code == 200
    descriptions = [c["description"] for c in resp.json()]
    assert descriptions == ["First PO", "Second PO"]


async def test_update_commitment(client: AsyncClient, project: Project, live_period: Period):
    el = await _create_element(client, project, live_period)
    created = await client.post("/api/v1/cost-commitments/", json={
        "cost_element_id": el["id"], "description": "Draft PO", "amount": "5000.00",
    })
    commitment_id = created.json()["id"]

    resp = await client.patch(f"/api/v1/cost-commitments/{commitment_id}", json={"amount": "5500.00"})
    assert resp.status_code == 200
    assert float(resp.json()["amount"]) == 5500.00


async def test_delete_commitment(client: AsyncClient, project: Project, live_period: Period):
    el = await _create_element(client, project, live_period)
    created = await client.post("/api/v1/cost-commitments/", json={
        "cost_element_id": el["id"], "description": "To be deleted", "amount": "1000.00",
    })
    commitment_id = created.json()["id"]

    assert (await client.delete(f"/api/v1/cost-commitments/{commitment_id}")).status_code == 204
    remaining = await client.get("/api/v1/cost-commitments/", params={"cost_element_id": el["id"]})
    assert remaining.json() == []


async def test_commitment_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    from app.models.cost_element import CostElement
    frozen_element = CostElement(
        project_id=project.id, period_id=frozen_period.id, code="CST-9002", description="Frozen element",
    )
    db.add(frozen_element)
    await db.commit()
    await db.refresh(frozen_element)

    resp = await client.post("/api/v1/cost-commitments/", json={
        "cost_element_id": str(frozen_element.id), "description": "Should be rejected", "amount": "1000.00",
    })
    assert resp.status_code == 422


async def test_commitment_for_unknown_element_404s(client: AsyncClient):
    resp = await client.post("/api/v1/cost-commitments/", json={
        "cost_element_id": str(uuid.uuid4()), "description": "Orphan commitment", "amount": "1000.00",
    })
    assert resp.status_code == 404
