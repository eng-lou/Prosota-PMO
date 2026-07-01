from __future__ import annotations

from httpx import AsyncClient

from app.models.project import Project


async def test_priority_criteria_auto_seeded_with_defaults(client: AsyncClient, project: Project):
    resp = await client.get("/api/v1/icd-criteria/priority", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 4
    labels = [c["label"] for c in sorted(data, key=lambda c: c["level"])]
    assert labels == ["Low", "Medium", "High", "Critical"]


async def test_severity_criteria_auto_seeded_with_defaults(client: AsyncClient, project: Project):
    resp = await client.get("/api/v1/icd-criteria/severity", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    labels = [c["label"] for c in sorted(resp.json(), key=lambda c: c["level"])]
    assert labels == ["Low", "Medium", "High", "Critical"]


async def test_quality_impact_criteria_auto_seeded_with_defaults(client: AsyncClient, project: Project):
    resp = await client.get("/api/v1/icd-criteria/quality_impact", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    labels = [c["label"] for c in sorted(resp.json(), key=lambda c: c["level"])]
    assert labels == ["None", "Low", "Medium", "High"]


async def test_criteria_seeded_only_once(client: AsyncClient, project: Project):
    first = await client.get("/api/v1/icd-criteria/priority", params={"project_id": str(project.id)})
    second = await client.get("/api/v1/icd-criteria/priority", params={"project_id": str(project.id)})
    assert len(first.json()) == len(second.json()) == 4
    assert {c["id"] for c in first.json()} == {c["id"] for c in second.json()}


async def test_update_criterion(client: AsyncClient, project: Project):
    criteria = (await client.get(
        "/api/v1/icd-criteria/priority", params={"project_id": str(project.id)}
    )).json()
    critical = next(c for c in criteria if c["label"] == "Critical")

    resp = await client.patch(f"/api/v1/icd-criteria/criterion/{critical['id']}", json={
        "description": "Drop everything — this blocks the critical path.",
    })
    assert resp.status_code == 200
    assert resp.json()["description"] == "Drop everything — this blocks the critical path."


async def test_criteria_dimensions_are_independent(client: AsyncClient, project: Project):
    """priority/severity/quality_impact each get their own 4 rows, not shared."""
    priority = (await client.get("/api/v1/icd-criteria/priority", params={"project_id": str(project.id)})).json()
    severity = (await client.get("/api/v1/icd-criteria/severity", params={"project_id": str(project.id)})).json()
    assert {c["id"] for c in priority}.isdisjoint({c["id"] for c in severity})


async def test_criteria_are_per_project(client: AsyncClient, project: Project, org):
    other_project_resp = await client.post("/api/v1/projects/", json={"name": "Other ICD Project"})
    other_project_id = other_project_resp.json()["id"]

    criteria_a = (await client.get("/api/v1/icd-criteria/priority", params={"project_id": str(project.id)})).json()
    criteria_b = (await client.get("/api/v1/icd-criteria/priority", params={"project_id": other_project_id})).json()
    assert {c["id"] for c in criteria_a}.isdisjoint({c["id"] for c in criteria_b})
