from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.period import Period
from app.models.project import Project
from app.models.risk import Risk


async def test_create_risk(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Ground contamination risk",
        "category": "Environmental",
        "probability": "0.30",
        "impact": "0.80",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Ground contamination risk"
    assert data["status"] == "open"
    assert float(data["probability"]) == 0.30
    assert "id" in data


async def test_create_risk_with_key_dates(client: AsyncClient, project: Project, live_period: Period):
    """date_raised (Date Identified), expected_impact_date, last_reviewed_date,
    and date_closed — matches the prototype's General tab date fields."""
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Ground contamination risk",
        "date_raised": "2026-05-02",
        "expected_impact_date": "2026-08-15",
        "last_reviewed_date": "2026-06-30",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["date_raised"] == "2026-05-02"
    assert data["expected_impact_date"] == "2026-08-15"
    assert data["last_reviewed_date"] == "2026-06-30"
    assert data["date_closed"] is None


async def test_date_closed_set_on_update(client: AsyncClient, project: Project, live_period: Period):
    create = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Risk to be closed",
    })
    risk_id = create.json()["id"]

    resp = await client.patch(f"/api/v1/risks/{risk_id}", json={
        "status": "closed",
        "date_closed": "2026-07-01",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "closed"
    assert resp.json()["date_closed"] == "2026-07-01"


async def test_create_risk_with_statement_and_ownership_fields(
    client: AsyncClient, project: Project, live_period: Period
):
    """Cause -> title -> Effect -> Rationale risk-statement structure, plus Theme
    (category) + Area (second RBS dimension) and risk_owner. See RISK_MODULE_PLAN.md Phase 1."""
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Supply Chain Delays",
        "category": "Schedule",
        "area": "Vendor",
        "risk_owner": "S. Wilson",
        "cause": "Delay of critical components from overseas manufacturers.",
        "effect": "Increased budget due to standing time for idle resources.",
        "rationale": "Supplier has reported reduced shipment schedules.",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["category"] == "Schedule"
    assert data["area"] == "Vendor"
    assert data["risk_owner"] == "S. Wilson"
    assert data["cause"] == "Delay of critical components from overseas manufacturers."
    assert data["effect"] == "Increased budget due to standing time for idle resources."
    assert data["rationale"] == "Supplier has reported reduced shipment schedules."


async def test_three_point_estimate_stores_min_most_likely_max(
    client: AsyncClient, project: Project, live_period: Period
):
    """Min/Most Likely/Max are all stored; EMV uses only the most-likely value —
    matches the prototype's Quantitative Analysis tab 3-point estimate."""
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Supply chain delay",
        "probability": "0.35",
        "cost_min": "50000.00",
        "cost_most_likely": "120000.00",
        "cost_max": "340000.00",
        "schedule_min_days": 7,
        "schedule_most_likely_days": 21,
        "schedule_max_days": 63,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert float(data["cost_min"]) == 50000.00
    assert float(data["cost_most_likely"]) == 120000.00
    assert float(data["cost_max"]) == 340000.00
    assert data["schedule_min_days"] == 7
    assert data["schedule_max_days"] == 63
    assert float(data["emv_cost"]) == -42000.00  # -(0.35 x 120000) — most-likely only


async def test_emv_computed_from_probability_and_cost_most_likely(
    client: AsyncClient, project: Project, live_period: Period
):
    """EMV = Probability x Impact (PMBOK7 / Rita Mulcahy). Impact here is a real
    monetary/duration value, not the qualitative 0-1 impact score. Default risk_type
    is 'threat', so EMV cost is negative (erodes budget) and EMV schedule is positive
    (adds days) — see test_emv_sign_convention_for_opportunities for the reverse."""
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Supply chain delay",
        "probability": "0.65",
        "cost_most_likely": "40000.00",
        "schedule_most_likely_days": 20,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["risk_type"] == "threat"
    assert float(data["emv_cost"]) == -26000.00  # -(0.65 x 40000)
    assert float(data["emv_schedule_days"]) == 13.00  # +(0.65 x 20) — threat adds days


async def test_residual_rating_computed_independently_of_inherent(
    client: AsyncClient, project: Project, live_period: Period
):
    """Inherent (pre-mitigation) and residual (post-mitigation target) ratings are
    computed independently — matches the prototype's Qualitative Analysis tab."""
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Supply chain delay",
        "probability": "0.60",
        "impact": "0.80",
        "probability_residual": "0.20",
        "impact_residual": "0.40",
        "rating_narrative": "Post-mitigation target assumes dual-sourcing is in place.",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert float(data["rating"]) == 0.48  # inherent: 0.60 x 0.80
    assert float(data["rating_residual"]) == 0.08  # residual: 0.20 x 0.40
    assert data["rating_narrative"] == "Post-mitigation target assumes dual-sourcing is in place."


async def test_residual_rating_missing_when_not_assessed_yet(
    client: AsyncClient, project: Project, live_period: Period
):
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Newly identified risk",
        "probability": "0.60",
        "impact": "0.80",
    })
    assert resp.status_code == 201
    assert resp.json()["rating_residual"] is None


async def test_emv_sign_convention_for_opportunities(
    client: AsyncClient, project: Project, live_period: Period
):
    """Opportunities are the mirror image: positive cost EMV (adds budget headroom),
    negative schedule EMV (saves days) — matches the book's own worked examples."""
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Bulk discount opportunity",
        "risk_type": "opportunity",
        "probability": "0.20",
        "cost_most_likely": "10000.00",
        "schedule_most_likely_days": 10,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert float(data["emv_cost"]) == 2000.00  # +(0.20 x 10000)
    assert float(data["emv_schedule_days"]) == -2.00  # -(0.20 x 10) — opportunity saves days


async def test_response_strategy_must_match_risk_type(
    client: AsyncClient, project: Project, live_period: Period
):
    """'exploit' is an opportunity-only strategy — invalid on a threat."""
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Bad combination",
        "risk_type": "threat",
        "response_strategy": "exploit",
    })
    assert resp.status_code == 422


async def test_response_strategy_valid_for_matching_risk_type(
    client: AsyncClient, project: Project, live_period: Period
):
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Correct combination",
        "risk_type": "opportunity",
        "response_strategy": "exploit",
    })
    assert resp.status_code == 201
    assert resp.json()["response_strategy"] == "exploit"


async def test_update_rejects_response_strategy_mismatched_with_existing_risk_type(
    client: AsyncClient, project: Project, live_period: Period
):
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Threat risk",
        "risk_type": "threat",
    })
    risk_id = resp.json()["id"]

    update = await client.patch(f"/api/v1/risks/{risk_id}", json={"response_strategy": "exploit"})
    assert update.status_code == 422


async def test_rating_computed_from_probability_and_qualitative_impact(
    client: AsyncClient, project: Project, live_period: Period
):
    """rating is the qualitative heat-map score (probability x impact, both 0-1) —
    independent of cost_most_likely/schedule_most_likely_days and never accepted as input."""
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Design change risk",
        "probability": "0.60",
        "impact": "0.40",
        "rating": "0.99",  # should be ignored — rating is always computed
    })
    assert resp.status_code == 201
    data = resp.json()
    assert float(data["rating"]) == 0.24  # 0.60 x 0.40, not the submitted 0.99


async def test_emv_missing_when_inputs_absent(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Risk with no quantitative estimate yet",
        "probability": "0.50",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["emv_cost"] is None
    assert data["emv_schedule_days"] is None


async def test_emv_recomputed_on_update(client: AsyncClient, project: Project, live_period: Period):
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Weather delay risk",
        "probability": "0.50",
        "cost_most_likely": "10000.00",
    })
    risk_id = resp.json()["id"]
    assert float(resp.json()["emv_cost"]) == -5000.00  # threat (default) -> negative

    updated = await client.patch(f"/api/v1/risks/{risk_id}", json={"cost_most_likely": "20000.00"})
    assert float(updated.json()["emv_cost"]) == -10000.00  # -(0.50 x 20000), recomputed


async def test_list_risks_by_project(client: AsyncClient, project: Project, live_period: Period):
    for title in ["Risk A", "Risk B", "Risk C"]:
        await client.post("/api/v1/risks/", json={
            "project_id": str(project.id),
            "period_id": str(live_period.id),
            "title": title,
        })

    resp = await client.get("/api/v1/risks/", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    assert len(resp.json()) == 3


async def test_list_risks_filter_by_period(
    client: AsyncClient, db: AsyncSession, project: Project, live_period: Period, frozen_period: Period
):
    await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Live period risk",
    })
    frozen_risk = Risk(project_id=project.id, period_id=frozen_period.id, code="RSK-9001", title="Frozen period risk")
    db.add(frozen_risk)
    await db.commit()

    resp = await client.get("/api/v1/risks/", params={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
    })
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Live period risk"


async def test_get_risk(client: AsyncClient, project: Project, live_period: Period):
    create = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Programme delay risk",
    })
    risk_id = create.json()["id"]

    resp = await client.get(f"/api/v1/risks/{risk_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Programme delay risk"


async def test_get_risk_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/risks/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_update_risk(client: AsyncClient, project: Project, live_period: Period):
    create = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Original risk",
        "status": "open",
    })
    risk_id = create.json()["id"]

    resp = await client.patch(f"/api/v1/risks/{risk_id}", json={
        "status": "mitigated",
        "mitigation_status": "complete",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "mitigated"
    assert data["mitigation_status"] == "complete"
    assert data["title"] == "Original risk"  # unchanged


async def test_mitigation_status_accepts_realistic_length_narrative(
    client: AsyncClient, project: Project, live_period: Period
):
    """Regression: mitigation_status was originally varchar(50), which broke on any
    real narrative text — it's a status narrative like contingency_plan, not a
    short enum code, so it must accept arbitrarily long text like the other narrative fields."""
    long_status = (
        "Additional intrusive ground investigations commissioned. Environmental "
        "consultant engaged. Early contractor involvement reviewing excavation "
        "methodology and contaminated material disposal routes. Contingency "
        "allowance included within programme and budget."
    )
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "Ground contamination risk",
        "mitigation_status": long_status,
    })
    assert resp.status_code == 201
    assert resp.json()["mitigation_status"] == long_status


async def test_delete_risk(client: AsyncClient, project: Project, live_period: Period):
    create = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(live_period.id),
        "title": "To be deleted",
    })
    risk_id = create.json()["id"]

    resp = await client.delete(f"/api/v1/risks/{risk_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/risks/{risk_id}")
    assert resp.status_code == 404


async def test_create_rejects_frozen_period(client: AsyncClient, project: Project, frozen_period: Period):
    resp = await client.post("/api/v1/risks/", json={
        "project_id": str(project.id),
        "period_id": str(frozen_period.id),
        "title": "Should be rejected",
    })
    assert resp.status_code == 422
    assert "frozen" in resp.json()["detail"].lower()


async def test_update_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    risk = Risk(project_id=project.id, period_id=frozen_period.id, code="RSK-9002", title="Frozen risk")
    db.add(risk)
    await db.commit()
    await db.refresh(risk)

    resp = await client.patch(f"/api/v1/risks/{risk.id}", json={"status": "closed"})
    assert resp.status_code == 422


async def test_delete_rejects_frozen_period(
    client: AsyncClient, db: AsyncSession, project: Project, frozen_period: Period
):
    risk = Risk(project_id=project.id, period_id=frozen_period.id, code="RSK-9003", title="Frozen risk")
    db.add(risk)
    await db.commit()
    await db.refresh(risk)

    resp = await client.delete(f"/api/v1/risks/{risk.id}")
    assert resp.status_code == 422
