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
        title="Underground service clash",
        status="open",
        priority="high",
        severity="high",
        owner="Site Manager",
    )
    assert item["item_type"] == "issue"
    assert item["severity"] == "high"
    assert item["cost_impact"] is None
    assert item["decision_maker"] is None


async def test_create_issue_with_issue_log_fields(client: AsyncClient, project: Project, live_period: Period):
    """description, raised_by, due_date, resolution — matches Rita Mulcahy Ch. 6's
    canonical Issue Log structure (Figure 6.7)."""
    item = await _create(client, project, live_period,
        item_type="issue",
        title="Underground service clash",
        description="450mm water main discovered running through proposed pile location.",
        raised_by="M. Azra",
        owner="Civil Lead",
        due_date="2026-05-25",
        severity="high",
    )
    assert item["description"] == "450mm water main discovered running through proposed pile location."
    assert item["raised_by"] == "M. Azra"
    assert item["owner"] == "Civil Lead"
    assert item["due_date"] == "2026-05-25"
    assert item["resolution"] is None


async def test_resolve_issue_sets_resolution(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period, item_type="issue", title="Drainage issue", severity="low")
    resp = await client.patch(f"/api/v1/icd-items/{item['id']}", json={
        "status": "closed",
        "closed_date": "2026-06-01",
        "resolution": "Additional pump installed; standing water cleared within 24 hours.",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "closed"
    assert resp.json()["resolution"] == "Additional pump installed; standing water cleared within 24 hours."


async def test_issue_rejects_change_fields(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "item_type": "issue",
        "title": "Bad issue",
        "cost_impact": "50000.00",  # change field on an issue
    })
    assert resp.status_code == 422


async def test_issue_rejects_decision_fields(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "item_type": "issue",
        "title": "Bad issue",
        "decision_maker": "Client",  # decision field on an issue
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Change
# ---------------------------------------------------------------------------

async def test_create_change(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period,
        item_type="change",
        title="Diversion of 450mm water main",
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
        "title": "Bad change",
        "severity": "high",  # issue field on a change
    })
    assert resp.status_code == 422


async def test_create_change_with_change_control_fields(client: AsyncClient, project: Project, live_period: Period):
    """change_type, contract_reference, cost_claim, eot_claim_days, quality_impact —
    Integrated Change Control (PMBOK Ch. 4)."""
    item = await _create(client, project, live_period,
        item_type="change",
        title="Diversion of 450mm water main",
        change_type="variation",
        contract_reference="NEC3 ECC Clause 60.1(12). CE-009 submitted 10/05/2024.",
        cost_impact="75000.00",
        cost_claim="72000.00",
        schedule_impact_days=14,
        eot_claim_days=10,
        quality_impact="low",
    )
    assert item["change_type"] == "variation"
    assert item["contract_reference"] == "NEC3 ECC Clause 60.1(12). CE-009 submitted 10/05/2024."
    assert float(item["cost_claim"]) == 72000.00
    assert item["eot_claim_days"] == 10
    assert item["quality_impact"] == "low"
    assert item["ccb_decision"] is None


async def test_ccb_approve_change(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period, item_type="change", title="Extra piling", cost_impact="20000.00")
    resp = await client.patch(f"/api/v1/icd-items/{item['id']}", json={
        "status": "approved", "ccb_decision": "approved",
    })
    assert resp.status_code == 200
    assert resp.json()["ccb_decision"] == "approved"


async def test_ccb_reject_requires_reason_relationship(client: AsyncClient, project: Project, live_period: Period):
    """rejection_reason only makes sense once the CCB has actually rejected the change."""
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "item_type": "change",
        "title": "Bad change",
        "cost_impact": "1000.00",
        "rejection_reason": "Not required",  # no ccb_decision at all
    })
    assert resp.status_code == 422


async def test_ccb_reject_with_reason(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period,
        item_type="change", title="Speculative change", cost_impact="5000.00",
        ccb_decision="rejected", rejection_reason="Not within contract scope; client to raise separately.",
    )
    assert item["ccb_decision"] == "rejected"
    assert item["rejection_reason"] == "Not within contract scope; client to raise separately."


async def test_change_control_fields_rejected_on_issue(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "item_type": "issue",
        "title": "Bad issue",
        "change_type": "variation",  # change field on an issue
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------

async def test_create_decision(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period,
        item_type="decision",
        title="Approve additional piling works",
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


async def test_create_decision_with_if_late_consequence(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period,
        item_type="decision",
        title="Approve additional piling works",
        decision_maker="Client Representative",
        required_by="2026-08-01",
        if_late_consequence="Piling rig demobilises 2026-08-05; remobilisation adds 3 weeks and £45,000.",
    )
    assert item["if_late_consequence"] == "Piling rig demobilises 2026-08-05; remobilisation adds 3 weeks and £45,000."


async def test_if_late_consequence_rejected_on_issue(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "item_type": "issue",
        "title": "Bad issue",
        "if_late_consequence": "Should not be allowed here",
    })
    assert resp.status_code == 422


async def test_decision_rejects_change_fields(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "item_type": "decision",
        "title": "Bad decision",
        "schedule_impact_days": 7,  # change field on a decision
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Shared CRUD and filtering
# ---------------------------------------------------------------------------

async def test_list_all_types(client: AsyncClient, project: Project, live_period: Period):
    await _create(client, project, live_period, item_type="issue", title="Issue A", severity="low")
    await _create(client, project, live_period, item_type="change", title="Change A", cost_impact="10000.00")
    await _create(client, project, live_period, item_type="decision", title="Decision A", decision_maker="PM")

    resp = await client.get("/api/v1/icd-items/", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    assert len(resp.json()) == 3


async def test_filter_by_item_type(client: AsyncClient, project: Project, live_period: Period):
    await _create(client, project, live_period, item_type="issue", title="Issue A", severity="medium")
    await _create(client, project, live_period, item_type="issue", title="Issue B", severity="high")
    await _create(client, project, live_period, item_type="change", title="Change A", cost_impact="5000.00")

    issues = (await client.get("/api/v1/icd-items/", params={
        "project_id": str(project.id),
        "item_type": "issue",
    })).json()
    assert len(issues) == 2
    assert all(i["item_type"] == "issue" for i in issues)


async def test_get_icd_item(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period, item_type="issue", title="Critical issue", severity="critical")
    resp = await client.get(f"/api/v1/icd-items/{item['id']}")
    assert resp.status_code == 200
    assert resp.json()["severity"] == "critical"


async def test_get_icd_item_not_found(client: AsyncClient):
    assert (await client.get(f"/api/v1/icd-items/{uuid.uuid4()}")).status_code == 404


async def test_update_icd_item(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period, item_type="issue", title="Low issue", severity="low", status="open")
    resp = await client.patch(f"/api/v1/icd-items/{item['id']}", json={"status": "closed", "severity": "medium"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "closed"
    assert resp.json()["severity"] == "medium"


async def test_delete_icd_item(client: AsyncClient, project: Project, live_period: Period):
    item = await _create(client, project, live_period, item_type="decision", title="Decision to delete", decision_maker="Architect")
    assert (await client.delete(f"/api/v1/icd-items/{item['id']}")).status_code == 204
    assert (await client.get(f"/api/v1/icd-items/{item['id']}")).status_code == 404


async def test_create_rejects_frozen_period(client: AsyncClient, project: Project, frozen_period: Period):
    resp = await client.post("/api/v1/icd-items/", json={
        "project_id": str(project.id),
        "period_id": str(frozen_period.id),
        "item_type": "issue",
        "title": "Frozen period issue",
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
    change = await _create(client, project, live_period, item_type="change", title="Water main diversion", cost_impact="50000.00")
    issue = await _create(client, project, live_period, item_type="issue", title="Water main clash", severity="high")

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
