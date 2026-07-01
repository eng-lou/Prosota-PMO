from __future__ import annotations

from httpx import AsyncClient

from app.models.project import Project


async def test_probability_criteria_auto_seeded_with_defaults(
    client: AsyncClient, project: Project
):
    """First access to a project's criteria seeds the 5 standard bands, matching
    the prototype's Criteria & Thresholds tab exactly."""
    resp = await client.get("/api/v1/risk-criteria/probability", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    labels = [c["label"] for c in sorted(data, key=lambda c: c["level"])]
    assert labels == ["Very Low", "Low", "Medium", "High", "Very High"]
    medium = next(c for c in data if c["label"] == "Medium")
    assert float(medium["min_probability"]) == 0.25
    assert float(medium["max_probability"]) == 0.50


async def test_impact_criteria_auto_seeded_with_defaults(client: AsyncClient, project: Project):
    resp = await client.get("/api/v1/risk-criteria/impact", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    high = next(c for c in data if c["label"] == "High")
    assert float(high["min_cost"]) == 500_000.00
    assert float(high["max_cost"]) == 1_000_000.00
    assert high["min_schedule_days"] == 28
    assert high["max_schedule_days"] == 56


async def test_criteria_seeded_only_once(client: AsyncClient, project: Project):
    """A second GET doesn't re-seed or duplicate rows."""
    first = await client.get("/api/v1/risk-criteria/probability", params={"project_id": str(project.id)})
    second = await client.get("/api/v1/risk-criteria/probability", params={"project_id": str(project.id)})
    assert len(first.json()) == len(second.json()) == 5
    assert {c["id"] for c in first.json()} == {c["id"] for c in second.json()}


async def test_update_probability_criterion(client: AsyncClient, project: Project):
    criteria = (await client.get(
        "/api/v1/risk-criteria/probability", params={"project_id": str(project.id)}
    )).json()
    medium = next(c for c in criteria if c["label"] == "Medium")

    resp = await client.patch(f"/api/v1/risk-criteria/probability/{medium['id']}", json={
        "min_probability": "0.30", "max_probability": "0.60",
    })
    assert resp.status_code == 200
    assert float(resp.json()["min_probability"]) == 0.30
    assert float(resp.json()["max_probability"]) == 0.60


async def test_update_impact_criterion(client: AsyncClient, project: Project):
    criteria = (await client.get(
        "/api/v1/risk-criteria/impact", params={"project_id": str(project.id)}
    )).json()
    critical = next(c for c in criteria if c["label"] == "Critical")

    resp = await client.patch(f"/api/v1/risk-criteria/impact/{critical['id']}", json={
        "min_cost": "2000000.00",
    })
    assert resp.status_code == 200
    assert float(resp.json()["min_cost"]) == 2_000_000.00


async def test_criteria_are_per_project(client: AsyncClient, project: Project, org):
    """A second project gets its own independent set of default criteria."""
    other_project_resp = await client.post("/api/v1/projects/", json={"name": "Other Project"})
    other_project_id = other_project_resp.json()["id"]

    criteria_a = (await client.get(
        "/api/v1/risk-criteria/probability", params={"project_id": str(project.id)}
    )).json()
    criteria_b = (await client.get(
        "/api/v1/risk-criteria/probability", params={"project_id": other_project_id}
    )).json()
    assert {c["id"] for c in criteria_a}.isdisjoint({c["id"] for c in criteria_b})
