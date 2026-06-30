from __future__ import annotations

import uuid

from httpx import AsyncClient

from app.models.organisation import Organisation
from app.models.user import User


async def _create(client: AsyncClient, **kwargs) -> dict:
    resp = await client.post("/api/v1/projects/", json={"name": "Test Project", **kwargs})
    assert resp.status_code == 201, resp.json()
    return resp.json()


async def test_create_project(client: AsyncClient):
    p = await _create(client, client_name="Acme Corp")
    assert p["name"] == "Test Project"
    assert p["client_name"] == "Acme Corp"
    assert p["status"] == "active"


async def test_list_projects(client: AsyncClient):
    await _create(client, name="Project A")
    await _create(client, name="Project B")
    resp = await client.get("/api/v1/projects/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_get_project(client: AsyncClient):
    p = await _create(client)
    resp = await client.get(f"/api/v1/projects/{p['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == p["id"]


async def test_get_project_not_found(client: AsyncClient):
    assert (await client.get(f"/api/v1/projects/{uuid.uuid4()}")).status_code == 404


async def test_update_project(client: AsyncClient):
    p = await _create(client)
    resp = await client.patch(f"/api/v1/projects/{p['id']}", json={"status": "archived"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "archived"


async def test_delete_project(client: AsyncClient):
    p = await _create(client)
    assert (await client.delete(f"/api/v1/projects/{p['id']}")).status_code == 204
    assert (await client.get(f"/api/v1/projects/{p['id']}")).status_code == 404


async def test_get_me(client: AsyncClient, user: User):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == user.email
    assert resp.json()["role"] == "admin"


async def test_create_and_list_periods(client: AsyncClient):
    p = await _create(client)
    period_resp = await client.post("/api/v1/periods/", json={
        "project_id": p["id"],
        "period_label": "Period 1",
        "freeze_status": "live",
    })
    assert period_resp.status_code == 201

    list_resp = await client.get("/api/v1/periods/", params={"project_id": p["id"]})
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["period_label"] == "Period 1"
