from __future__ import annotations

import uuid
from datetime import date

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import Period
from app.models.project import Project
from app.models.risk import Risk


async def _create_risk(client: AsyncClient, project: Project, period: Period) -> dict:
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(period.id),
        "title": "Supply chain delay",
    })
    assert resp.status_code == 201, resp.json()
    return resp.json()


async def test_create_reassessment_logs_note_and_timestamp(
    client: AsyncClient, project: Project, live_period: Period
):
    risk = await _create_risk(client, project, live_period)
    resp = await client.post("/api/v1/risk-reassessments/", json={
        "risk_id": risk["id"],
        "note": "Probability revised from 0.65 to 0.30 following supplier confirmation of dual-sourcing.",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["risk_id"] == risk["id"]
    assert "Probability revised" in data["note"]
    assert "reviewed_at" in data


async def test_create_reassessment_bumps_last_reviewed_date(
    client: AsyncClient, project: Project, live_period: Period
):
    """Logging a reassessment is itself a review event — should auto-update the
    parent risk's last_reviewed_date, distinct from the one-off rating_narrative."""
    risk = await _create_risk(client, project, live_period)
    assert risk["last_reviewed_date"] is None

    await client.post("/api/v1/risk-reassessments/", json={
        "risk_id": risk["id"],
        "note": "Reviewed at monthly risk board — no change to rating.",
    })

    updated = await client.get(f"/api/v1/risks/{risk['id']}")
    assert updated.json()["last_reviewed_date"] == date.today().isoformat()


async def test_list_reassessments_for_risk_newest_first(
    client: AsyncClient, project: Project, live_period: Period
):
    risk = await _create_risk(client, project, live_period)
    await client.post("/api/v1/risk-reassessments/", json={"risk_id": risk["id"], "note": "First review"})
    await client.post("/api/v1/risk-reassessments/", json={"risk_id": risk["id"], "note": "Second review"})

    resp = await client.get("/api/v1/risk-reassessments/", params={"risk_id": risk["id"]})
    assert resp.status_code == 200
    notes = [r["note"] for r in resp.json()]
    assert notes == ["Second review", "First review"]


async def test_reassessment_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    frozen_risk = Risk(project_id=project.id, period_id=frozen_period.id, code="RSK-9001", title="Frozen risk")
    db.add(frozen_risk)
    await db.commit()
    await db.refresh(frozen_risk)

    resp = await client.post("/api/v1/risk-reassessments/", json={
        "risk_id": str(frozen_risk.id), "note": "Should be rejected",
    })
    assert resp.status_code == 422


async def test_reassessment_for_unknown_risk_404s(client: AsyncClient):
    resp = await client.post("/api/v1/risk-reassessments/", json={
        "risk_id": str(uuid.uuid4()), "note": "Orphan note",
    })
    assert resp.status_code == 404


async def test_update_reassessment_note(client: AsyncClient, project: Project, live_period: Period):
    risk = await _create_risk(client, project, live_period)
    created = await client.post("/api/v1/risk-reassessments/", json={
        "risk_id": risk["id"], "note": "Original wording",
    })
    entry_id = created.json()["id"]

    resp = await client.patch(f"/api/v1/risk-reassessments/{entry_id}", json={"note": "Corrected wording"})
    assert resp.status_code == 200
    assert resp.json()["note"] == "Corrected wording"


async def test_delete_reassessment(client: AsyncClient, project: Project, live_period: Period):
    risk = await _create_risk(client, project, live_period)
    created = await client.post("/api/v1/risk-reassessments/", json={
        "risk_id": risk["id"], "note": "To be deleted",
    })
    entry_id = created.json()["id"]

    assert (await client.delete(f"/api/v1/risk-reassessments/{entry_id}")).status_code == 204
    remaining = await client.get("/api/v1/risk-reassessments/", params={"risk_id": risk["id"]})
    assert remaining.json() == []


async def test_update_reassessment_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    frozen_risk = Risk(project_id=project.id, period_id=frozen_period.id, code="RSK-9002", title="Frozen risk")
    db.add(frozen_risk)
    await db.commit()
    await db.refresh(frozen_risk)

    # Bypass the API's own frozen-period rejection on create by inserting the
    # reassessment directly, to test that update/delete independently enforce it.
    from app.models.risk_reassessment import RiskReassessment
    entry = RiskReassessment(risk_id=frozen_risk.id, note="Pre-existing note")
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    resp = await client.patch(f"/api/v1/risk-reassessments/{entry.id}", json={"note": "Edited"})
    assert resp.status_code == 422

    resp = await client.delete(f"/api/v1/risk-reassessments/{entry.id}")
    assert resp.status_code == 422
