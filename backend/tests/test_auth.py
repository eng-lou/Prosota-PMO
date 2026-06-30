from __future__ import annotations

import uuid

from httpx import AsyncClient


async def test_health_requires_no_auth(raw_client: AsyncClient):
    resp = await raw_client.get("/health")
    assert resp.status_code == 200


async def test_protected_route_rejects_no_token(raw_client: AsyncClient):
    resp = await raw_client.get(f"/api/v1/activities/?project_id={uuid.uuid4()}")
    assert resp.status_code == 403  # HTTPBearer returns 403 when no credentials at all


async def test_protected_route_rejects_bad_token(raw_client: AsyncClient):
    resp = await raw_client.get(
        f"/api/v1/activities/?project_id={uuid.uuid4()}",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401


async def test_authed_client_can_reach_protected_route(client: AsyncClient):
    # client fixture overrides auth — proves the override works end-to-end
    resp = await client.get(f"/api/v1/activities/?project_id={uuid.uuid4()}")
    assert resp.status_code == 200
