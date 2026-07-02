from __future__ import annotations

from httpx import AsyncClient

from app.models.project import Project


async def test_criteria_auto_seeded_with_defaults(client: AsyncClient, project: Project):
    resp = await client.get("/api/v1/cost-variance-criteria/", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 4
    labels = [c["label"] for c in sorted(data, key=lambda c: c["level"])]
    assert labels == ["Saving", "On Budget", "Monitor", "Over Budget"]
    on_budget = next(c for c in data if c["label"] == "On Budget")
    assert float(on_budget["min_pct"]) == -1.00
    assert float(on_budget["max_pct"]) == 1.00


async def test_criteria_seeded_only_once(client: AsyncClient, project: Project):
    first = await client.get("/api/v1/cost-variance-criteria/", params={"project_id": str(project.id)})
    second = await client.get("/api/v1/cost-variance-criteria/", params={"project_id": str(project.id)})
    assert len(first.json()) == len(second.json()) == 4
    assert {c["id"] for c in first.json()} == {c["id"] for c in second.json()}


async def test_update_criterion(client: AsyncClient, project: Project):
    criteria = (await client.get(
        "/api/v1/cost-variance-criteria/", params={"project_id": str(project.id)}
    )).json()
    over_budget = next(c for c in criteria if c["label"] == "Over Budget")

    resp = await client.patch(f"/api/v1/cost-variance-criteria/{over_budget['id']}", json={"min_pct": "10.00"})
    assert resp.status_code == 200
    assert float(resp.json()["min_pct"]) == 10.00


async def test_criteria_are_per_project(client: AsyncClient, project: Project, org):
    other_project_resp = await client.post("/api/v1/projects/", json={"name": "Other Cost Project"})
    other_project_id = other_project_resp.json()["id"]

    criteria_a = (await client.get("/api/v1/cost-variance-criteria/", params={"project_id": str(project.id)})).json()
    criteria_b = (await client.get("/api/v1/cost-variance-criteria/", params={"project_id": other_project_id})).json()
    assert {c["id"] for c in criteria_a}.isdisjoint({c["id"] for c in criteria_b})
