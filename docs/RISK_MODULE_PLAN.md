# Risk Module — Consolidated Plan

**Purpose:** Before continuing to other modules, bring the Risk Register to a properly considered state — reconciling three sources that have never been read side by side until now: (1) what the prototype and scope/business-case documents already specified, (2) what PMBOK7/PMP best practice (Rita Mulcahy Ch. 12, "Risks and Issues") requires or recommends, and (3) what's actually built today. This doc is the reconciliation, a gap analysis, and a proposed phased plan. Nothing in Section D is implemented yet — it's here for review and prioritisation before any code changes.

---

## A. What the Prototype + Scope Document Already Specified

Source: `docs/ProsotaPMO_Project_Scope_Document.docx` Section 4.4, `docs/ProsotaPMO_Business_Case_v3.docx`, and the actual prototype markup (`docs/prototype/prosota-pmo_7.html`, Risk Register view + Risk Detail panel).

> "A full ISO 31000-aligned risk register with qualitative and quantitative analysis." — scope doc, 4.4

### A.1 Register (list) view
- Columns: ID, Name, Status, **Theme** (category), **Area** (a second, separate categorisation dimension — not currently in our schema, which only has one `category` field), Rating, Probability, Impact, EMV Cost, EMV Schedule
- Search, Filters, Group-by, saved view toggle ("C-3")
- Import/Export: Excel (.xlsx) and Risk Register XML (.xml)
- Print/Preview (dedicated modal, same pattern as Scheduling)

### A.2 Risk Detail — 6 tabs
1. **General** — Risk ID, Risk Name, Risk Status (Draft/Open/Closed/Last Reviewed), **Risk Owner**, Theme, Area, Date Identified, Last Reviewed, plus four free-text fields: **Cause**, **Description**, **Effect**, **Rationale/Assumptions** (this Cause→Description→Effect structure is a recognised risk-statement format, not decorative)
2. **Criteria & Thresholds** — an organisation-defined, editable **probability scale** (Very Low…Very High, each with a % range and description) and **impact scale** (Negligible…Critical, each with a £ range AND a schedule-week range) — i.e. the rating bands are configurable data, not hard-coded, and the risk's current position is highlighted against them. This is a direct implementation of what Rita Mulcahy calls the risk management plan's *"definitions of probability and impact"* (see B.2 below) — currently **completely missing** from our schema.
3. **Qualitative Analysis** — a real 5×5 colour-coded heat matrix, plus a **Pre-Mitigation (Inherent) Rating** vs **Post-Mitigation (Residual) Rating** side-by-side comparison with a narrative text box. We currently store exactly one probability/impact/rating triple — no inherent-vs-residual distinction at all.
4. **Quantitative Analysis** — **3-point estimates** (Minimum / Most Likely / Maximum) for both cost and schedule impact, feeding an EMV figure, plus a visual distribution curve, the probability used, and a list of linked schedule activities showing float consumed. This is a materially more sophisticated EMV model than the single-point `cost_impact` we just implemented this session — it's PERT/triangular-distribution style, not just `P × single-impact-value`.
5. **Mitigation & Response** — Response Type (**Reduce/Mitigate, Transfer, Accept, Avoid, Exploit** — a mix of threat *and* opportunity strategies in one dropdown), Response Owner, Target Close Date, Response Status, Response Description, a **Contingency Plan** text field, and a repeatable list of individual **Mitigation Actions** (own ID like `MA-01`, owner, due date, status, and a % complete progress bar) — i.e. a one-to-many sub-record, not a single `mitigation_status` string.
6. **Linked** — the cross-module linking graph tab (this one we've already built and generalised further than the prototype, since ours supports genuine cross-type linking rather than same-type only).

### A.3 Dashboard / Export integration
- Controls Dashboard: "Top 5 Risks" table (EMV Cost + EMV Schedule columns), a risk exposure chart ("Risk EMV Exposure by Category"), heat matrix mirrored on the dashboard
- Export Center: `fact_risk` table with individual field-level export selection
- AI Setup Assistant can propose a **draft** risk (category, rating, probability, EMV) from an imported schedule — never auto-written, always Accept/Edit/Dismiss
- 8-slide report builder includes a dedicated "Risk Heat Matrix" slide

---

## B. What PMBOK7 / Rita Mulcahy Ch. 12 Requires or Recommends

Read directly, in full, this session (not just the EMV section). Organised by what's genuinely actionable in software vs exam-only theory.

### B.1 Core distinction the whole chapter hinges on
**Qualitative** (ordinal, unitless, for triage/prioritisation) vs **Quantitative** (real currency/duration, for reserves) analysis are separate, non-interchangeable steps, done in that order. We already fixed the EMV side of this bug this session (see `PROJECT_STATE.md` session log). The **qualitative side still has a gap**: no configurable probability/impact *definitions* (see B.2) and no inherent-vs-residual split (see B.5).

### B.2 Risk Management Plan — "definitions of probability and impact"
> "Would everyone who rates the probability of a particular risk a 7 on a 1-to-10 scale mean the same thing?... The definitions and the probability and impact matrix help standardize these interpretations." — Ch. 12

This is exactly the prototype's "Criteria & Thresholds" tab. **Currently missing entirely** — our probability/impact are just raw 0–1 numbers with no organisational scale surfaced anywhere.

### B.3 Risk categories / Risk Breakdown Structure (RBS)
A hierarchical categorisation (by source: technical, external, organisational, project management, etc.) to make sure risk identification doesn't miss whole categories. The prototype's **Theme + Area** two-dimensional categorisation is a simplified RBS. We currently have one flat `category` string.

### B.4 Risk parameters (urgency, dormancy, manageability, strategic impact)
Used to decide which risks skip ahead in prioritisation regardless of raw rating. **Not in the prototype's fields either** — likely genuinely out of scope for v1, flagging for completeness only.

### B.5 Threats vs Opportunities — the biggest structural gap
- Every risk is either a **threat** (negative) or **opportunity** (positive) — we have no such field.
- Response strategies differ by type: **Avoid/Mitigate/Transfer/Escalate/Accept** for threats; **Exploit/Enhance/Share/Escalate/Accept** for opportunities. The prototype's single response dropdown (`Reduce/Transfer/Accept/Avoid/Exploit`) already mixes both — a bug **in the prototype itself**, not something to blindly copy.
- EMV sign convention: opportunities are positive EMV, threats negative, when shown individually (e.g. on a decision tree) — but when rolled up into a **contingency reserve**, threats *increase* the reserve and opportunities *decrease* it (reserve = Σthreat EMV − Σopportunity EMV). We have no reserve rollup at all yet (no Controls Dashboard).

### B.6 Watch List
Risks that ranked low enough in qualitative analysis to not warrant a full response plan yet, but are tracked and revisited. This is a **status/bucket**, not a separate table — could be a `status` value or boolean flag. Not in current schema.

### B.7 Inherent vs Residual Risk (pre/post-mitigation)
> "there is usually residual risk on a project" — and the prototype's Qualitative Analysis tab already visualises this directly (pre-mitigation heat-matrix position vs post-mitigation target). **Not modelled at all currently** — we have one rating, not two.

### B.8 Risk response strategies, contingency/fallback plans, secondary risks, risk triggers, risk owner
- **Risk owner**: someone assigned to watch for and lead the response to a specific risk. Prototype has this (`Risk Owner` field); we don't.
- **Contingency plan** (what to do if it happens) vs **fallback plan** (what to do if the contingency plan doesn't work) — two distinct fields. Prototype has a contingency plan field; no fallback plan field currently anywhere.
- **Secondary risks**: new risks created *by* a response (e.g. outsourcing to mitigate a skills risk creates a vendor-reliability risk). Not modelled — would most naturally be a `record_links` edge (risk → risk, "causes") rather than a new field, since we already have the linking graph.
- **Risk triggers**: early-warning signs that a risk is about to occur. Not modelled; likely a free-text field would suffice for v1.

### B.9 Decision tree analysis / sensitivity analysis / Monte Carlo
Advanced quantitative techniques for comparing multiple response options or overall project risk exposure. These operate **across multiple risks or options**, not on a single risk record — more naturally a Controls Dashboard / reporting feature than a Risk Register CRUD feature. Flagging for later, not proposing to build into the register itself.

### B.10 Monitoring: risk reviews/audits, reassessment, risk report
Process discipline (recurring review, closing risks and returning their reserve, updating the risk report) more than a data-model requirement — mostly satisfied by the register just existing and being editable, plus (eventually) a period-based history/audit trail, which ties into the Period Manager work already flagged as outstanding.

---

## C. Gap Analysis — Current State vs A + B

| Capability | Prototype/Scope | PMBOK Ch.12 | Currently built? |
|---|---|---|---|
| Basic CRUD, category, status, mitigation status | Yes | — | ✅ Yes |
| Cross-module linking | Yes | (implicit via secondary risks) | ✅ Yes, and more general than the prototype |
| Human-readable reference codes | Yes (R1012 etc.) | — | ✅ Yes (RSK-0001 etc., this session) |
| EMV correctly calculated (P × real impact) | Yes | Yes — explicit | ✅ Fixed this session |
| Qualitative rating (P × impact score) | Yes | Yes | ✅ Fixed this session |
| Configurable probability/impact criteria & thresholds | Yes (dedicated tab) | Yes — "definitions of probability and impact" | ✅ Built (Phase 5) — project-level, auto-seeded with prototype's own default bands |
| Two-dimensional categorisation (Theme + Area / RBS) | Yes | Yes (RBS concept) | ✅ Built (Phase 1) |
| Risk owner | Yes | Yes | ✅ Built (Phase 1) |
| Cause / Description / Effect / Rationale structure | Yes | (implicit — risk statement quality) | ✅ Built (Phase 1) |
| Inherent (pre-mitigation) vs residual (post-mitigation) rating | Yes | Yes | ✅ Built (Phase 3), incl. real 5×5 heat-matrix component |
| 3-point (Min/ML/Max) quantitative estimate | Yes | (decision tree/sensitivity analysis touch on this) | ✅ Built (Phase 6) — EMV uses most-likely value only |
| Response strategy type, correctly split threat vs opportunity | Yes (but mixed, buggy) | Yes — explicit, separate lists | ✅ Built (Phase 2), corrected vs the prototype's mixed dropdown |
| Contingency plan vs fallback plan (two fields) | Contingency only | Both, explicitly distinct | ✅ Built (Phase 4) |
| Mitigation actions as a sub-list with owner/due/status/progress | Yes | (implicit in response planning) | ✅ Built (Phase 4) — own `risk_mitigation_actions` table, MA-01 style codes per risk |
| Threat vs opportunity flag | No explicit field, but implied | Yes — fundamental | ✅ Built (Phase 2), incl. correct EMV sign convention (cost and schedule signs are asymmetric — see Ch. 12 worked examples) |
| Watch list | Implicit via status | Yes — explicit concept | ❌ Missing |
| Secondary risks | No | Yes | ❌ Missing (would use `record_links`) |
| Risk triggers | No | Yes | ❌ Missing |
| Contingency reserve rollup (Σthreats − Σopportunities) | Dashboard chart implies it | Yes — explicit | ❌ Missing (needs Dashboard anyway) |
| Import/Export, Print/Preview | Yes | — | ❌ Not built for any module yet (known, tracked separately) |

---

## D. Phased Plan — Status: All 6 Phases Complete (2026-07-01)

Maro said "go ahead" without individually answering the three open questions below — the following judgment calls were made and applied consistently; flag if any should be revisited.

**Phase 1 — Risk statement & ownership quality** ✅ Done
- Added `risk_owner`, `cause`, `effect`, `rationale` (kept `title` as the short name)
- Added `area` alongside existing `category` ("theme") for the RBS-lite Theme+Area split

**Phase 2 — Threat vs Opportunity** ✅ Done
- Added `risk_type: 'threat' | 'opportunity'`
- Split response strategy options by type (Avoid/Mitigate/Transfer/Escalate/Accept vs Exploit/Enhance/Share/Escalate/Accept), validated server-side against `risk_type` — corrects the prototype's mixed dropdown
- EMV sign convention handled automatically from `risk_type` — and turned out to be **asymmetric between cost and schedule** per the book's own worked examples: a threat's cost EMV is negative (erodes budget) but its schedule EMV is positive (adds days); an opportunity is the mirror image. Locked in with dedicated tests for both directions.

**Phase 3 — Inherent vs Residual rating** ✅ Done
- Added `probability_residual`/`impact_residual`/`rating_residual` (computed) alongside the existing inherent triple, plus `rating_narrative`
- Built a real 5×5 heat-matrix component (`frontend/src/components/HeatMatrix.tsx`), shown twice per risk (inherent + residual) in the expanded row

**Phase 4 — Mitigation Actions as a real sub-list** ✅ Done
- New `risk_mitigation_actions` table, own `MA-01`/`MA-02`... codes sequential **per risk** (not per project — a dedicated generator, since the shared `next_code()` helper is project-scoped)
- Full CRUD (`frontend/src/modules/risks/MitigationActions.tsx`), nested in the risk's expanded row
- Added `contingency_plan` and `fallback_plan` text fields to the risk itself

**Phase 5 — Configurable Criteria & Thresholds** ✅ Done
- **Decision:** project-level (not org-level) — matches every other project-scoped table in this codebase; org-level would need new cross-project settings architecture that doesn't exist yet
- Two dedicated tables (`risk_probability_criteria`, `risk_impact_criteria` — impact needs both a cost AND a schedule range per level, probability doesn't), auto-seeded with the prototype's exact default bands on first access per project
- Collapsible panel at the top of the Risk Register (`CriteriaThresholds.tsx`), inline-editable

**Phase 6 — 3-point quantitative estimates** ✅ Done
- **Decision:** EMV uses only the Most Likely value, not a PERT-weighted average — the reference material's own worked EMV examples are all single-point, so a weighted formula isn't something verifiable against source; would be guessing at math not in the book
- Renamed `cost_impact`/`schedule_impact_days` → `cost_most_likely`/`schedule_most_likely_days` (safe rename, nothing using the old names was committed yet) and added `cost_min`/`cost_max`/`schedule_min_days`/`schedule_max_days` as range context

**Deferred, not part of "getting the risk module to a good state" — belongs to other modules:**
- Contingency reserve rollup, decision tree analysis, sensitivity/tornado charts, Monte Carlo → Controls Dashboard work
- Watch list, secondary risks (via `record_links`), risk triggers → not built; still genuine gaps, revisit if they start to matter in practice
- Import/Export, Print/Preview → cross-module concern already tracked, not risk-specific

All 6 phases verified: 97 backend tests passing (up from 71 at session start), `tsc --noEmit` shows zero new errors throughout, backend restarted clean after every migration. **Not yet confirmed by a human in the browser** — same standing rule as every other feature this session.
