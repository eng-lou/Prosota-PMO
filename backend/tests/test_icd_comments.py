from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import Period
from app.models.project import Project
from app.models.user import User


async def _create_item(client: AsyncClient, project: Project, period: Period) -> dict:
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(period.id),
        "item_type": "issue",
        "title": "Underground service clash",
        "severity": "high",
    })
    assert resp.status_code == 201, resp.json()
    return resp.json()


async def test_create_comment_uses_real_authenticated_user(
    client: AsyncClient, project: Project, live_period: Period, user: User
):
    item = await _create_item(client, project, live_period)
    resp = await client.post("/api/v1/icd-comments/", json={
        "icd_item_id": item["id"], "body": "Confirmed with the utility company this morning.",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["body"] == "Confirmed with the utility company this morning."
    assert data["author_id"] == str(user.id)
    assert data["author_name"] == user.display_name


async def test_list_comments_oldest_first(client: AsyncClient, project: Project, live_period: Period):
    item = await _create_item(client, project, live_period)
    await client.post("/api/v1/icd-comments/", json={"icd_item_id": item["id"], "body": "First comment"})
    await client.post("/api/v1/icd-comments/", json={"icd_item_id": item["id"], "body": "Second comment"})

    resp = await client.get("/api/v1/icd-comments/", params={"icd_item_id": item["id"]})
    assert resp.status_code == 200
    bodies = [c["body"] for c in resp.json()]
    assert bodies == ["First comment", "Second comment"]


async def test_update_own_comment(client: AsyncClient, project: Project, live_period: Period):
    item = await _create_item(client, project, live_period)
    created = await client.post("/api/v1/icd-comments/", json={"icd_item_id": item["id"], "body": "Original"})
    comment_id = created.json()["id"]

    resp = await client.patch(f"/api/v1/icd-comments/{comment_id}", json={"body": "Corrected"})
    assert resp.status_code == 200
    assert resp.json()["body"] == "Corrected"


async def test_delete_own_comment(client: AsyncClient, project: Project, live_period: Period):
    item = await _create_item(client, project, live_period)
    created = await client.post("/api/v1/icd-comments/", json={"icd_item_id": item["id"], "body": "To be deleted"})
    comment_id = created.json()["id"]

    assert (await client.delete(f"/api/v1/icd-comments/{comment_id}")).status_code == 204
    remaining = await client.get("/api/v1/icd-comments/", params={"icd_item_id": item["id"]})
    assert remaining.json() == []


async def test_comment_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    from app.models.icd_item import IcdItem
    frozen_item = IcdItem(
        project_id=project.id, period_id=frozen_period.id, item_type="issue",
        code="ISS-9004", title="Frozen issue", severity="low",
    )
    db.add(frozen_item)
    await db.commit()
    await db.refresh(frozen_item)

    resp = await client.post("/api/v1/icd-comments/", json={
        "icd_item_id": str(frozen_item.id), "body": "Should be rejected",
    })
    assert resp.status_code == 422


async def test_comment_for_unknown_item_404s(client: AsyncClient):
    resp = await client.post("/api/v1/icd-comments/", json={
        "icd_item_id": str(uuid.uuid4()), "body": "Orphan comment",
    })
    assert resp.status_code == 404


async def test_cannot_edit_or_delete_someone_elses_comment(
    client: AsyncClient, db: AsyncSession, project: Project, live_period: Period, user: User
):
    from app.models.icd_comment import IcdComment

    item = await _create_item(client, project, live_period)
    other_author = User(
        org_id=user.org_id, email="other@prosota.com", auth0_sub="auth0|other-user",
        display_name="Other User", role="member",
    )
    db.add(other_author)
    await db.commit()
    await db.refresh(other_author)

    comment = IcdComment(
        icd_item_id=item["id"], author_id=other_author.id,
        author_name=other_author.display_name, body="Someone else's comment",
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    assert (await client.patch(f"/api/v1/icd-comments/{comment.id}", json={"body": "Hijacked"})).status_code == 403
    assert (await client.delete(f"/api/v1/icd-comments/{comment.id}")).status_code == 403
