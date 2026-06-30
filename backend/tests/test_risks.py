from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import Period
from app.models.project import Project
from app.models.risk import Risk


async def test_create_risk(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Ground contamination risk",
        "category": "Environmental",
        "probability": "0.30",
        "impact": "0.80",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Ground contamination risk"
    assert data["status"] == "open"
    assert float(data["probability"]) == 0.30
    assert "id" in data


async def test_list_risks_by_project(client: AsyncClient, project: Project, live_period: Period):
    for title in ["Risk A", "Risk B", "Risk C"]:
        await client.post("/api/v1/risks/", json={
            "project_id": str(project.id),
            "period_id": str(live_period.id),
            "title": title,
        })

    resp = await client.get("/api/v1/risks/", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    assert len(resp.json()) == 3


async def test_list_risks_filter_by_period(
    client: AsyncClient, db: AsyncSession, project: Project, live_period: Period, frozen_period: Period
):
    await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Live period risk",
    })
    frozen_risk = Risk(project_id=project.id, period_id=frozen_period.id, title="Frozen period risk")
    db.add(frozen_risk)
    await db.commit()

    resp = await client.get("/api/v1/risks/", params={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
    })
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Live period risk"


async def test_get_risk(client: AsyncClient, project: Project, live_period: Period):
    create = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Programme delay risk",
    })
    risk_id = create.json()["id"]

    resp = await client.get(f"/api/v1/risks/{risk_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Programme delay risk"


async def test_get_risk_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/risks/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_update_risk(client: AsyncClient, project: Project, live_period: Period):
    create = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Original risk",
        "status": "open",
    })
    risk_id = create.json()["id"]

    resp = await client.patch(f"/api/v1/risks/{risk_id}", json={
        "status": "mitigated",
        "mitigation_status": "complete",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "mitigated"
    assert data["mitigation_status"] == "complete"
    assert data["title"] == "Original risk"  # unchanged


async def test_delete_risk(client: AsyncClient, project: Project, live_period: Period):
    create = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "To be deleted",
    })
    risk_id = create.json()["id"]

    resp = await client.delete(f"/api/v1/risks/{risk_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/risks/{risk_id}")
    assert resp.status_code == 404


async def test_create_rejects_frozen_period(client: AsyncClient, project: Project, frozen_period: Period):
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(frozen_period.id),
        "title": "Should be rejected",
    })
    assert resp.status_code == 422
    assert "frozen" in resp.json()["detail"].lower()


async def test_update_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    risk = Risk(project_id=project.id, period_id=frozen_period.id, title="Frozen risk")
    db.add(risk)
    await db.commit()
    await db.refresh(risk)

    resp = await client.patch(f"/api/v1/risks/{risk.id}", json={"status": "closed"})
    assert resp.status_code == 422


async def test_delete_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    risk = Risk(project_id=project.id, period_id=frozen_period.id, title="Frozen risk")
    db.add(risk)
    await db.commit()
    await db.refresh(risk)

    resp = await client.delete(f"/api/v1/risks/{risk.id}")
    assert resp.status_code == 422
