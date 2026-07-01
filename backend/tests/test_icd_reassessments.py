from __future__ import annotations

import uuid
from datetime import date

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import Period
from app.models.project import Project


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


async def test_create_reassessment_logs_note_and_timestamp(
    client: AsyncClient, project: Project, live_period: Period
):
    item = await _create_item(client, project, live_period)
    resp = await client.post("/api/v1/icd-reassessments/", json={
        "icd_item_id": item["id"],
        "note": "Severity escalated from medium to high following client escalation.",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["icd_item_id"] == item["id"]
    assert "Severity escalated" in data["note"]
    assert "reviewed_at" in data


async def test_create_reassessment_bumps_last_reviewed_date(
    client: AsyncClient, project: Project, live_period: Period
):
    item = await _create_item(client, project, live_period)
    assert item["last_reviewed_date"] is None

    await client.post("/api/v1/icd-reassessments/", json={
        "icd_item_id": item["id"],
        "note": "Reviewed at weekly ICD board — no change.",
    })

    updated = await client.get(f"/api/v1/icd-items/{item['id']}")
    assert updated.json()["last_reviewed_date"] == date.today().isoformat()


async def test_list_reassessments_for_item_newest_first(
    client: AsyncClient, project: Project, live_period: Period
):
    item = await _create_item(client, project, live_period)
    await client.post("/api/v1/icd-reassessments/", json={"icd_item_id": item["id"], "note": "First review"})
    await client.post("/api/v1/icd-reassessments/", json={"icd_item_id": item["id"], "note": "Second review"})

    resp = await client.get("/api/v1/icd-reassessments/", params={"icd_item_id": item["id"]})
    assert resp.status_code == 200
    notes = [r["note"] for r in resp.json()]
    assert notes == ["Second review", "First review"]


async def test_reassessment_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    from app.models.icd_item import IcdItem
    frozen_item = IcdItem(
        project_id=project.id, period_id=frozen_period.id, item_type="issue",
        code="ISS-9001", title="Frozen issue", severity="low",
    )
    db.add(frozen_item)
    await db.commit()
    await db.refresh(frozen_item)

    resp = await client.post("/api/v1/icd-reassessments/", json={
        "icd_item_id": str(frozen_item.id), "note": "Should be rejected",
    })
    assert resp.status_code == 422


async def test_reassessment_for_unknown_item_404s(client: AsyncClient):
    resp = await client.post("/api/v1/icd-reassessments/", json={
        "icd_item_id": str(uuid.uuid4()), "note": "Orphan note",
    })
    assert resp.status_code == 404


async def test_update_reassessment_note(client: AsyncClient, project: Project, live_period: Period):
    item = await _create_item(client, project, live_period)
    created = await client.post("/api/v1/icd-reassessments/", json={
        "icd_item_id": item["id"], "note": "Original wording",
    })
    entry_id = created.json()["id"]

    resp = await client.patch(f"/api/v1/icd-reassessments/{entry_id}", json={"note": "Corrected wording"})
    assert resp.status_code == 200
    assert resp.json()["note"] == "Corrected wording"


async def test_delete_reassessment(client: AsyncClient, project: Project, live_period: Period):
    item = await _create_item(client, project, live_period)
    created = await client.post("/api/v1/icd-reassessments/", json={
        "icd_item_id": item["id"], "note": "To be deleted",
    })
    entry_id = created.json()["id"]

    assert (await client.delete(f"/api/v1/icd-reassessments/{entry_id}")).status_code == 204
    remaining = await client.get("/api/v1/icd-reassessments/", params={"icd_item_id": item["id"]})
    assert remaining.json() == []


async def test_update_reassessment_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    from app.models.icd_item import IcdItem
    from app.models.icd_reassessment import IcdReassessment

    frozen_item = IcdItem(
        project_id=project.id, period_id=frozen_period.id, item_type="issue",
        code="ISS-9002", title="Frozen issue", severity="low",
    )
    db.add(frozen_item)
    await db.commit()
    await db.refresh(frozen_item)

    entry = IcdReassessment(icd_item_id=frozen_item.id, note="Pre-existing note")
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    resp = await client.patch(f"/api/v1/icd-reassessments/{entry.id}", json={"note": "Edited"})
    assert resp.status_code == 422

    resp = await client.delete(f"/api/v1/icd-reassessments/{entry.id}")
    assert resp.status_code == 422
