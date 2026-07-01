from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import Period
from app.models.project import Project


async def _create_item(client: AsyncClient, project: Project, period: Period, title: str = "Underground service clash") -> dict:
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(period.id),
        "item_type": "issue",
        "title": title,
        "severity": "high",
    })
    assert resp.status_code == 201, resp.json()
    return resp.json()


async def test_create_action_item(client: AsyncClient, project: Project, live_period: Period):
    item = await _create_item(client, project, live_period)
    resp = await client.post("/api/v1/icd-action-items/", json={
        "icd_item_id": item["id"],
        "description": "Confirm diversion route with utility",
        "owner": "S. Wilson",
        "due_date": "2026-08-01",
        "status": "in_progress",
        "pct_complete": 60,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "ACT-01"
    assert data["description"] == "Confirm diversion route with utility"
    assert data["pct_complete"] == 60


async def test_action_item_codes_sequential_per_item(client: AsyncClient, project: Project, live_period: Period):
    item = await _create_item(client, project, live_period)
    codes = []
    for desc in ["Confirm diversion route", "Notify utility company", "Update drawings"]:
        resp = await client.post("/api/v1/icd-action-items/", json={
            "icd_item_id": item["id"], "description": desc,
        })
        codes.append(resp.json()["code"])
    assert codes == ["ACT-01", "ACT-02", "ACT-03"]


async def test_action_item_codes_reset_per_item(client: AsyncClient, project: Project, live_period: Period):
    """Each ICD item gets its own ACT-01, ACT-02... — not a project-wide sequence."""
    item_a = await _create_item(client, project, live_period, "Issue A")
    item_b = await _create_item(client, project, live_period, "Issue B")

    resp_a = await client.post("/api/v1/icd-action-items/", json={
        "icd_item_id": item_a["id"], "description": "Action for issue A",
    })
    resp_b = await client.post("/api/v1/icd-action-items/", json={
        "icd_item_id": item_b["id"], "description": "Action for issue B",
    })
    assert resp_a.json()["code"] == "ACT-01"
    assert resp_b.json()["code"] == "ACT-01"


async def test_list_action_items_for_item(client: AsyncClient, project: Project, live_period: Period):
    item = await _create_item(client, project, live_period)
    for desc in ["Action 1", "Action 2"]:
        await client.post("/api/v1/icd-action-items/", json={
            "icd_item_id": item["id"], "description": desc,
        })

    resp = await client.get("/api/v1/icd-action-items/", params={"icd_item_id": item["id"]})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_update_action_item_progress(client: AsyncClient, project: Project, live_period: Period):
    item = await _create_item(client, project, live_period)
    created = await client.post("/api/v1/icd-action-items/", json={
        "icd_item_id": item["id"], "description": "Notify utility company", "pct_complete": 0,
    })
    action_id = created.json()["id"]

    resp = await client.patch(f"/api/v1/icd-action-items/{action_id}", json={
        "status": "complete", "pct_complete": 100,
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "complete"
    assert resp.json()["pct_complete"] == 100


async def test_delete_action_item(client: AsyncClient, project: Project, live_period: Period):
    item = await _create_item(client, project, live_period)
    created = await client.post("/api/v1/icd-action-items/", json={
        "icd_item_id": item["id"], "description": "To be deleted",
    })
    action_id = created.json()["id"]

    assert (await client.delete(f"/api/v1/icd-action-items/{action_id}")).status_code == 204
    assert (await client.get(f"/api/v1/icd-action-items/{action_id}")).status_code == 404


async def test_action_item_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    """Action items inherit the period-freeze check from their parent ICD item."""
    from app.models.icd_item import IcdItem
    frozen_item = IcdItem(
        project_id=project.id, period_id=frozen_period.id, item_type="issue",
        code="ISS-9003", title="Frozen issue", severity="low",
    )
    db.add(frozen_item)
    await db.commit()
    await db.refresh(frozen_item)

    resp = await client.post("/api/v1/icd-action-items/", json={
        "icd_item_id": str(frozen_item.id), "description": "Should be rejected",
    })
    assert resp.status_code == 422


async def test_get_action_item_not_found(client: AsyncClient):
    assert (await client.get(f"/api/v1/icd-action-items/{uuid.uuid4()}")).status_code == 404
