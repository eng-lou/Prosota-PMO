from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.period import Period
from app.models.project import Project


async def test_create_activity(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/activities/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "task_name": "Excavation works",
        "is_critical": True,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["task_name"] == "Excavation works"
    assert data["is_critical"] is True
    assert "id" in data
    assert data["project_id"] == str(project.id)


async def test_list_activities_by_project(client: AsyncClient, project: Project, live_period: Period):
    for name in ["Piling", "Groundworks"]:
        await client.post("/api/v1/activities/", json={
            "project_id": str(project.id),
            "period_id": str(live_period.id),
            "task_name": name,
        })

    resp = await client.get("/api/v1/activities/", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_list_activities_excludes_other_projects(
    client: AsyncClient, db: AsyncSession, project: Project, live_period: Period, org
):
    await client.post("/api/v1/activities/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "task_name": "Belongs to project A",
    })

    other_project = Project(org_id=org.id, name="Other Project")
    db.add(other_project)
    await db.commit()
    await db.refresh(other_project)

    resp = await client.get("/api/v1/activities/", params={"project_id": str(other_project.id)})
    assert resp.status_code == 200
    assert len(resp.json()) == 0


async def test_list_activities_filter_by_period(
    client: AsyncClient, db: AsyncSession, project: Project, live_period: Period, frozen_period: Period
):
    await client.post("/api/v1/activities/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "task_name": "In live period",
    })
    # Insert directly to frozen period (bypassing API freeze check)
    frozen_activity = Activity(project_id=project.id, period_id=frozen_period.id, task_name="In frozen period")
    db.add(frozen_activity)
    await db.commit()

    resp = await client.get("/api/v1/activities/", params={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
    })
    assert resp.status_code == 200
    names = [a["task_name"] for a in resp.json()]
    assert names == ["In live period"]


async def test_get_activity(client: AsyncClient, project: Project, live_period: Period):
    create = await client.post("/api/v1/activities/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "task_name": "Steel erection",
    })
    activity_id = create.json()["id"]

    resp = await client.get(f"/api/v1/activities/{activity_id}")
    assert resp.status_code == 200
    assert resp.json()["task_name"] == "Steel erection"


async def test_get_activity_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/activities/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_update_activity(client: AsyncClient, project: Project, live_period: Period):
    create = await client.post("/api/v1/activities/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "task_name": "Original name",
        "pct_complete": "25.00",
    })
    activity_id = create.json()["id"]

    resp = await client.patch(f"/api/v1/activities/{activity_id}", json={
        "task_name": "Updated name",
        "pct_complete": "75.00",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["task_name"] == "Updated name"
    assert float(data["pct_complete"]) == 75.0


async def test_update_activity_partial(client: AsyncClient, project: Project, live_period: Period):
    create = await client.post("/api/v1/activities/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "task_name": "Original",
        "is_critical": False,
    })
    activity_id = create.json()["id"]

    resp = await client.patch(f"/api/v1/activities/{activity_id}", json={"is_critical": True})
    assert resp.status_code == 200
    data = resp.json()
    assert data["task_name"] == "Original"  # unchanged
    assert data["is_critical"] is True      # updated


async def test_delete_activity(client: AsyncClient, project: Project, live_period: Period):
    create = await client.post("/api/v1/activities/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "task_name": "To be deleted",
    })
    activity_id = create.json()["id"]

    resp = await client.delete(f"/api/v1/activities/{activity_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/activities/{activity_id}")
    assert resp.status_code == 404


async def test_create_rejects_frozen_period(client: AsyncClient, project: Project, frozen_period: Period):
    resp = await client.post("/api/v1/activities/", json={
        "project_id": str(project.id),
        "period_id": str(frozen_period.id),
        "task_name": "Should be rejected",
    })
    assert resp.status_code == 422
    assert "frozen" in resp.json()["detail"].lower()


async def test_update_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    activity = Activity(project_id=project.id, period_id=frozen_period.id, task_name="Frozen activity")
    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    resp = await client.patch(f"/api/v1/activities/{activity.id}", json={"task_name": "Attempt edit"})
    assert resp.status_code == 422


async def test_delete_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    activity = Activity(project_id=project.id, period_id=frozen_period.id, task_name="Frozen activity")
    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    resp = await client.delete(f"/api/v1/activities/{activity.id}")
    assert resp.status_code == 422
