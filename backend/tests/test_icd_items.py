from __future__ import annotations

import uuid

from httpx import AsyncClient

from app.models.period import Period
from app.models.project import Project


async def _create(client: AsyncClient, project: Project, period: Period, **kwargs) -> dict:
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(period.id),
        **kwargs,
    })
    assert resp.status_code == 201, resp.json()
    return resp.json()


# ---------------------------------------------------------------------------
# Issue
# ---------------------------------------------------------------------------

async def test_create_issue(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period,
        item_type="issue",
        status="open",
        priority="high",
        severity="high",
        owner="Site Manager",
    )
    assert item["item_type"] == "issue"
    assert item["severity"] == "high"
    assert item["cost_impact"] is None
    assert item["decision_maker"] is None


async def test_issue_rejects_change_fields(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "item_type": "issue",
        "cost_impact": "50000.00",  # change field on an issue
    })
    assert resp.status_code == 422


async def test_issue_rejects_decision_fields(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "item_type": "issue",
        "decision_maker": "Client",  # decision field on an issue
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Change
# ---------------------------------------------------------------------------

async def test_create_change(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period,
        item_type="change",
        status="open",
        priority="high",
        cost_impact="75000.00",
        schedule_impact_days=14,
        owner="Project Manager",
    )
    assert item["item_type"] == "change"
    assert float(item["cost_impact"]) == 75000.00
    assert item["schedule_impact_days"] == 14
    assert item["severity"] is None
    assert item["decision_maker"] is None


async def test_change_rejects_issue_fields(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "item_type": "change",
        "severity": "high",  # issue field on a change
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------

async def test_create_decision(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period,
        item_type="decision",
        status="open",
        decision_maker="Client Representative",
        required_by="2026-08-01",
        owner="Design Manager",
    )
    assert item["item_type"] == "decision"
    assert item["decision_maker"] == "Client Representative"
    assert item["required_by"] == "2026-08-01"
    assert item["severity"] is None
    assert item["cost_impact"] is None


async def test_decision_rejects_change_fields(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "item_type": "decision",
        "schedule_impact_days": 7,  # change field on a decision
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Shared CRUD and filtering
# ---------------------------------------------------------------------------

async def test_list_all_types(client: AsyncClient, project: Project, live_period: Period):
    await _create(client, project, live_period, item_type="issue", severity="low")
    await _create(client, project, live_period, item_type="change", cost_impact="10000.00")
    await _create(client, project, live_period, item_type="decision", decision_maker="PM")

    resp = await client.get("/api/v1/icd-items/", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    assert len(resp.json()) == 3


async def test_filter_by_item_type(client: AsyncClient, project: Project, live_period: Period):
    await _create(client, project, live_period, item_type="issue", severity="medium")
    await _create(client, project, live_period, item_type="issue", severity="high")
    await _create(client, project, live_period, item_type="change", cost_impact="5000.00")

    issues = (await client.get("/api/v1/icd-items/", params={
        "project_id": str(project.id),
        "item_type": "issue",
    })).json()
    assert len(issues) == 2
    assert all(i["item_type"] == "issue" for i in issues)


async def test_get_icd_item(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period, item_type="issue", severity="critical")
    resp = await client.get(f"/api/v1/icd-items/{item['id']}")
    assert resp.status_code == 200
    assert resp.json()["severity"] == "critical"


async def test_get_icd_item_not_found(client: AsyncClient):
    assert (await client.get(f"/api/v1/icd-items/{uuid.uuid4()}")).status_code == 404


async def test_update_icd_item(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period, item_type="issue", severity="low", status="open")
    resp = await client.patch(f"/api/v1/icd-items/{item['id']}", json={"status": "closed", "severity": "medium"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "closed"
    assert resp.json()["severity"] == "medium"


async def test_delete_icd_item(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period, item_type="decision", decision_maker="Architect")
    assert (await client.delete(f"/api/v1/icd-items/{item['id']}")).status_code == 204
    assert (await client.get(f"/api/v1/icd-items/{item['id']}")).status_code == 404


async def test_create_rejects_frozen_period(client: AsyncClient, project: Project, frozen_period: Period):
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(frozen_period.id),
        "item_type": "issue",
        "severity": "low",
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Record links work across ICD sub-types
# ---------------------------------------------------------------------------

async def test_icd_items_linkable_as_typed_record_types(
    client: AsyncClient, project: Project, live_period: Period
):
    """A Change and an Issue can be linked; the link uses their ICD sub-type as the record_type."""
    change = await _create(client, project, live_period, item_type="change", cost_impact="50000.00")
    issue = await _create(client, project, live_period, item_type="issue", severity="high")

    link = (await client.post("/api/v1/record-links/", json={
        "source_type": "change",
        "source_id": change["id"],
        "target_type": "issue",
        "target_id": issue["id"],
        "link_type": "relates_to",
        "note": "Change request raised in response to this issue",
    })).json()

    assert link["source_type"] == "change"
    assert link["target_type"] == "issue"

    # Queryable from both sides
    from_change = (await client.get("/api/v1/record-links/", params={
        "record_type": "change", "record_id": change["id"],
    })).json()
    assert len(from_change) == 1

    from_issue = (await client.get("/api/v1/record-links/", params={
        "record_type": "issue", "record_id": issue["id"],
    })).json()
    assert len(from_issue) == 1
    assert from_issue[0]["id"] == from_change[0]["id"]
