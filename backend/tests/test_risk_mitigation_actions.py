from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import Period
from app.models.project import Project
from app.models.risk import Risk


async def _create_risk(client: AsyncClient, project: Project, period: Period, title: str = "Supply chain delay") -> dict:
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(period.id),
        "title": title,
    })
    assert resp.status_code == 201, resp.json()
    return resp.json()


async def test_create_mitigation_action(client: AsyncClient, project: Project, live_period: Period):
    risk = await _create_risk(client, project, live_period)
    resp = await client.post("/api/v1/risk-mitigation-actions/", json={
        "risk_id": risk["id"],
        "description": "Dual-source supplier",
        "owner": "S. Wilson",
        "due_date": "2026-08-01",
        "status": "in_progress",
        "pct_complete": 60,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "MA-01"
    assert data["description"] == "Dual-source supplier"
    assert data["pct_complete"] == 60


async def test_mitigation_action_codes_sequential_per_risk(
    client: AsyncClient, project: Project, live_period: Period
):
    risk = await _create_risk(client, project, live_period)
    codes = []
    for desc in ["Dual-source supplier", "Buffer stock agreement", "Weekly shipment calls"]:
        resp = await client.post("/api/v1/risk-mitigation-actions/", json={
            "risk_id": risk["id"],
            "description": desc,
        })
        codes.append(resp.json()["code"])
    assert codes == ["MA-01", "MA-02", "MA-03"]


async def test_mitigation_action_codes_reset_per_risk(
    client: AsyncClient, project: Project, live_period: Period
):
    """Each risk gets its own MA-01, MA-02... — not a project-wide sequence."""
    risk_a = await _create_risk(client, project, live_period, "Risk A")
    risk_b = await _create_risk(client, project, live_period, "Risk B")

    resp_a = await client.post("/api/v1/risk-mitigation-actions/", json={
        "risk_id": risk_a["id"], "description": "Action for risk A",
    })
    resp_b = await client.post("/api/v1/risk-mitigation-actions/", json={
        "risk_id": risk_b["id"], "description": "Action for risk B",
    })
    assert resp_a.json()["code"] == "MA-01"
    assert resp_b.json()["code"] == "MA-01"


async def test_list_mitigation_actions_for_risk(client: AsyncClient, project: Project, live_period: Period):
    risk = await _create_risk(client, project, live_period)
    for desc in ["Action 1", "Action 2"]:
        await client.post("/api/v1/risk-mitigation-actions/", json={
            "risk_id": risk["id"], "description": desc,
        })

    resp = await client.get("/api/v1/risk-mitigation-actions/", params={"risk_id": risk["id"]})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_update_mitigation_action_progress(client: AsyncClient, project: Project, live_period: Period):
    risk = await _create_risk(client, project, live_period)
    created = await client.post("/api/v1/risk-mitigation-actions/", json={
        "risk_id": risk["id"], "description": "Buffer stock agreement", "pct_complete": 0,
    })
    action_id = created.json()["id"]

    resp = await client.patch(f"/api/v1/risk-mitigation-actions/{action_id}", json={
        "status": "complete", "pct_complete": 100,
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "complete"
    assert resp.json()["pct_complete"] == 100


async def test_delete_mitigation_action(client: AsyncClient, project: Project, live_period: Period):
    risk = await _create_risk(client, project, live_period)
    created = await client.post("/api/v1/risk-mitigation-actions/", json={
        "risk_id": risk["id"], "description": "To be deleted",
    })
    action_id = created.json()["id"]

    assert (await client.delete(f"/api/v1/risk-mitigation-actions/{action_id}")).status_code == 204
    assert (await client.get(f"/api/v1/risk-mitigation-actions/{action_id}")).status_code == 404


async def test_mitigation_action_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    """Mitigation actions inherit the period-freeze check from their parent risk."""
    frozen_risk = Risk(project_id=project.id, period_id=frozen_period.id, code="RSK-9001", title="Frozen risk")
    db.add(frozen_risk)
    await db.commit()
    await db.refresh(frozen_risk)

    resp = await client.post("/api/v1/risk-mitigation-actions/", json={
        "risk_id": str(frozen_risk.id), "description": "Should be rejected",
    })
    assert resp.status_code == 422


async def test_get_mitigation_action_not_found(client: AsyncClient):
    assert (await client.get(f"/api/v1/risk-mitigation-actions/{uuid.uuid4()}")).status_code == 404
