# Cost Plan Module — Consolidated Plan

Same process as `docs/RISK_MODULE_PLAN.md` and `docs/ICD_MODULE_PLAN.md`: read the prototype's actual Cost Plan markup, read the scope document's Cost Plan section, read the relevant PMBOK/Rita Mulcahy chapter (Chapter 9, "Budget and Resources" — covers Estimate Costs, Determine Budget, Control Costs, and Earned Value Management), reconcile all three into one gap analysis, then propose a phased plan for review before implementing anything.

---

## A. What the Prototype + Scope Document Already Specify

### A.1 Elemental Cost Analysis table
8 elemental groups (Substructure, Superstructure, Fire Protection, Roofing & Cladding, Fitout, MEP, External Works, On Costs), each collapsible, group-level and line-item-level. Every line shows: **Total Cost, £/m², % of Total, Rev A Baseline, Variance, Status** (Approved / Over Budget / Saving / Monitor / Applied % / CR Pending / Credit / TBC).

### A.2 On Costs as genuine percentages
Prelims (15%), Construction Contingency (4%), Design Contingency (2%), OH&P (5.6%), Insurance (1.3%), plus a **Market Conditions Deduction (MCD) credit line — a negative percentage.**

### A.3 Cost Detail panel — 6 tabs (General / Budget & Versions / Forecast & Phasing / Actuals & Commitments / Variance & Narrative / Linked)
- **General**: Element ID, Description, Group, **Cost Owner**, **Status** dropdown, a **Scope/Specification Note** (long text) and a separate **Variance Commentary** (long text) — two distinct narrative fields, not one.
- **Budget & Versions**: a Rev A/B/C revision history table per element, plus a **Rate Card** — a repeatable Qty × Unit × Rate build-up sub-list (e.g. "Rig mobilisation ×1 @ £10,000", "CFA piles ×267 @ £576"...) with a computed element total and rate-revision flags.
- **Forecast & Phasing**: a period-by-period table (Planned/Forecast/Variance/Actuals/Commitments + a status dot) for the *same* line item across time.
- **Actuals & Commitments**: an invoice list (Actuals to Date), an **Open Commitments** sub-list (PO number + amount), and a real **Earned Value** panel — BCWP (EV), BCWS (PV), ACWP (AC), CPI, SPI, CV.
- **Variance & Narrative**: variance vs Rev A broken into Qty variance / Rate variance / Total variance, a Forecast-At-Completion figure, a period narrative textarea, and a **QS sign-off** (name + date).
- **Linked**: cross-module `record_links`, same as every other module.

### A.4 Right-hand Cost Summary panel
£/m² and £/Space unit-rate cards (needs project-level GFA and Space count), a full budget breakdown (Building Works / External Works / Total Construction / Prelims / Contingencies / OH&P / Insurance / MCD Credit / **TOTAL BUDGET**), a Rev A vs Rev C uplift box, and a ranked **Top Variance Drivers** list.

### A.5 Toolbar
Version selector (Rev A/B/C) + "Compare vs" dropdown, group filter, Filters button, Import/Export (.xlsx/.xml), Print/Preview — same pattern as Risk/ICD.

---

## B. What PMBOK7 / Rita Mulcahh Chapter 9 Adds

### B.1 Earned Value Management — the actual formulas (not just labels)
The prototype already *shows* BCWP/BCWS/ACWP/CPI/SPI as static numbers, but our current implementation has never computed any of them — `cpi`/`spi` exist as dead columns (correctly removed from manual entry last session, per [[feedback_pm_domain_accuracy]], but nothing replaced them). Ch. 9's full formula set:

| Term | Formula | Meaning |
|---|---|---|
| PV (Planned Value / BCWS) | — | Value of work planned to be done by now |
| EV (Earned Value / BCWP) | — | Value of work actually accomplished |
| AC (Actual Cost / ACWP) | — | Actual cost incurred |
| BAC (Budget at Completion) | — | Total approved budget |
| CV (Cost Variance) | EV − AC | Negative = over budget |
| SV (Schedule Variance) | EV − PV | Negative = behind schedule |
| CPI | EV / AC | <1 bad, >1 good — "$ of work per $ spent" |
| SPI | EV / PV | <1 bad, >1 good — "rate of progress vs plan" |
| EAC (typical variance, continues at current rate) | BAC / CPI | Most common EAC formula |
| EAC (atypical variance) | AC + (BAC − EV) | Used when past variance won't recur |
| ETC | EAC − AC | How much more it will cost to finish |
| VAC | BAC − EAC | How far over/under budget at completion |
| TCPI | (BAC − EV) / (BAC − AC) | Rate needed on remaining work to hit BAC |

**The missing ingredient is EV.** EV can't be computed without a measure of physical progress. Rita Ch. 9 confirms the standard technique for exactly this situation (no network-schedule integration available yet): **EV = BAC × % physical complete**, an estimate a cost engineer/QS assesses directly per cost line — this is real, standard practice, not a shortcut invented to avoid building Scheduling. Once a genuine `pct_complete` input exists (the same concept already used for Risk's mitigation actions and ICD's action items), every other EVM figure becomes a real, honest calculation instead of a placeholder.

### B.2 Cost baseline vs budget (BAC) vs reserves
BAC = the cost baseline (aggregated estimates + contingency reserves for identified risks). The **budget** additionally includes management reserve for unknown-unknowns, which is *not* part of the baseline used for EVM. Our current single `budget` field conflates these; for now, treating `budget` as BAC is a reasonable simplification (we have no separate management-reserve concept anywhere yet) — flagged as a scope limit, not silently glossed over.

### B.3 Determine Budget — cost aggregation is hierarchical
Activity estimates → work package → control account → project estimate → **+ contingency reserves = cost baseline** → **+ management reserve = budget**. Confirms On Costs (Prelims/Contingency/OH&P/Insurance) belong logically *inside* the cost baseline as legitimate line items, which is exactly how the prototype and our current `percentage`-type elements already model them — no change needed there.

### B.4 What's not worth chasing from the reference material here
Full multi-baseline/rebaseline governance (Rev A/B/C history) is really a Period Manager / formal-baseline-freeze concept, not something to bolt onto individual cost elements in isolation — flagged as an open question below rather than assumed.

---

## C. Gap Analysis

| Capability | Prototype/Scope | PMBOK Ch. 9 | Currently built? |
|---|---|---|---|
| Fixed/percentage dual-type elements, computed at query time | Yes | (implicit) | ✅ Yes |
| Human-readable reference codes (CST-) | Yes | — | ✅ Yes |
| Cross-module linking | Yes | (implicit) | ✅ Yes |
| Period-freeze enforcement | Yes | — | ✅ Yes |
| **`cost_owner`** | Yes ("Cost Owner: M. Azra") | (implicit accountability) | ❌ Missing |
| **`status`** (workflow: Approved/CR Pending/TBC/Credit) | Yes | — | ❌ Missing entirely — no status field at all today |
| Variance severity band (Over Budget/Monitor/On Budget/Saving) | Yes, shown as Status | (implicit — variance analysis) | ❌ Missing — conflated with `status` in the prototype; should be a *computed* badge against configurable thresholds, not a manual field (same reasoning as Risk's heat-map rating vs `status`) |
| **Scope/Specification Note** + **Variance Commentary** (two separate long-text fields) | Yes | (implicit) | ❌ Missing — only one `description` field exists, used as the short line title |
| **Real EVM** (`pct_complete` input; computed PV/EV/AC/CV/SV/CPI/SPI/EAC/ETC/VAC/TCPI) | Yes (shown as static numbers) | Yes — the whole chapter | ❌ Missing — `cpi`/`spi` are dead unused columns; no `pct_complete` exists anywhere |
| **`cost_per_m2`** exposed as *computed*, not manual entry | Implied (shown as a derived unit rate) | (implicit — same class of mistake as CPI/SPI) | ❌ Currently a **manual free-text field** — same mistake class already fixed once for Risk's EMV and once for Cost Plan's own CPI/SPI last session, never revisited for this field |
| Project-level GFA (m²) and Space count, for £/m² and £/Space | Yes | — | ❌ Missing — not on the `Project` model at all |
| **QS sign-off** (name + date) on the variance narrative | Yes | (implicit — approval/accountability) | ❌ Missing |
| **Rate Card** sub-list (Qty × Unit × Rate build-up per element) | Yes | (implicit — bottom-up estimating basis) | ❌ Missing — third occurrence of the "repeatable sub-list" pattern (after Risk Mitigation Actions, ICD Action Items) |
| **Open Commitments** sub-list (PO + amount) | Yes | Yes (referenced in Control Costs) | ❌ Missing |
| Negative percentage rate (MCD Credit) | Yes | — | ❌ **Actively rejected today** — `rate` schema has `ge=0`, blocking any credit-type percentage element |
| Configurable Cost Variance Thresholds (numeric bands → label) | Implied by Status categories | (implicit — analogous to Risk's impact criteria) | ❌ Missing — but same pattern already built twice for Risk (`RiskImpactCriterion`) |
| Cost Summary panel (£/m², £/Space, full budget breakdown, Rev A vs Rev C uplift, Top Variance Drivers) | Yes | — | ❌ Missing — pure client-side aggregation over already-loaded data, same complexity as Risk/ICD's KPI strips |
| Search/Filters/Group/Export/Print toolbar | Yes | — | ❌ Missing — same pattern already built twice, should generalise |
| Reassessment/history log ("what changed and why") | Not explicit in prototype, but same real-world need as Risk/ICD | (implicit — Control Costs is inherently iterative) | ❌ Missing — **third occurrence** of the identical Risk/ICD reassessment-log pattern; worth actually generalising into one shared implementation this time rather than copying a third time |
| Full Rev A/B/C revision history *per element* | Yes | (implicit — rebaselining via change control) | ❌ Missing — likely belongs with Period Manager's eventual baseline-freeze mechanism, not bolted onto individual elements now |
| Import (real file parsing) | Yes (prototype UI only) | — | ❌ Deliberately deferred, same as Risk/ICD |

---

## D. Proposed Phased Plan (for review — nothing implemented yet)

**Phase 1 — General-tab field gaps**
- Add `cost_owner` (String), `scope_note` (Text), `variance_commentary` (Text) to `CostElement`.
- Add `status` as a genuine workflow field: `approved | cr_pending | tbc | credit` (deliberately *not* including Over Budget/Saving/Monitor/On Budget/Applied % — see Phase 3).
- Add `qs_signoff_name` (String), `qs_signoff_date` (Date).

**Phase 2 — Real Earned Value Management**
- Add `pct_complete` (Integer 0–100) as a genuine manual input — the physical-progress assessment Ch. 9 confirms is the standard EV technique without schedule-network integration.
- Drop the dead `cpi`/`spi` stored columns; compute **PV = budget, AC = actuals, EV = budget × pct_complete/100, BAC = budget**, then CV/SV/CPI/SPI/EAC/ETC/VAC/TCPI server-side (never accepted as API input — same discipline as Risk's EMV fix). Guard all divisions against zero.
- Fix `cost_per_m2` to be **computed** (budget ÷ project GFA), not manual entry — same bug class as CPI/SPI and EMV, just never revisited for this field. Requires **Phase 2b**: add `gfa_m2` and `space_count` to the `Project` model (needed for £/m² and £/Space everywhere, not just this one field).
- Fix the `rate` field's validation to allow negative values (`ge=-1` not `ge=0`) so a percentage-type element can represent a genuine credit/deduction like MCD.

**Phase 3 — Configurable Cost Variance Thresholds (numeric bands, reusing Risk's Impact Criteria pattern)**
- New `cost_variance_criteria` table (project-scoped, level/label/min_pct/max_pct/description), auto-seeded with sensible defaults (e.g. ≥+5% Over Budget, +1–5% Monitor, ±1% On Budget, <−1% Saving).
- Frontend shows the variance band as a **computed badge**, not a stored value — resolves the Status-field overload identified in the gap analysis.

**Phase 4 — Rate Card sub-list**
- New `cost_rate_lines` table (`cost_element_id`, description, qty, unit, rate, computed total) — a repeatable Qty × Unit × Rate build-up per element, matching the prototype's Budget & Versions tab exactly.

**Phase 5 — Open Commitments sub-list**
- New `cost_commitments` table (`cost_element_id`, description/PO reference, amount) feeding the "Total Commitments" figure shown alongside EVM in Actuals & Commitments.

**Phase 6 — Cost Summary panel + Search/Filters/Group/Export/Print**
- A real, computed right-hand summary: £/m² and £/Space (from Phase 2b's project GFA/space fields), full budget breakdown by group, Rev A vs current uplift, and a ranked Top Variance Drivers list — pure client-side aggregation, same complexity as Risk/ICD's KPI strips.
- Generalise the Search/Filters(status/group/type)/Group-by/Export/Print toolbar already built twice for Risk and ICD.

**Phase 7 — Reassessment/history log — generalise this time**
- This would be the **third** near-identical implementation of the user-prompted reassessment-log pattern (Risk → ICD → Cost). Proposing to actually extract it now into one shared backend service (parametrised by parent table/FK) and one shared frontend component (parametrised by API path + trigger fields), rather than copying the pattern a third time. Flagged as an open question below rather than assumed.

**Explicitly deferred, with reasoning:**
- **Full Rev A/B/C revision history per element** — this is fundamentally a baseline-freeze/versioning concept that belongs with the not-yet-built Period Manager, not something to bolt onto individual cost elements in isolation. `rev_a_baseline` (already exists) remains the single reference point for variance until Period Manager exists.
- **Import (real file parsing)** — same reasoning as Risk/ICD: a bigger, separate task requiring real file-reading + field-mapping UI.
- **Management reserve as a concept distinct from the cost baseline** — noted in Section B.2, but no separate reserve mechanism exists anywhere in the app yet (mirrors the Risk Module's deferred reserve-rollup, both waiting on the future Controls Dashboard).

---

## Decisions Confirmed by Maro (2026-07-01)

1. **Status field split** — confirmed: `status` stays a manual workflow field (`approved | cr_pending | tbc | credit`); Over Budget/Monitor/On Budget/Saving becomes a computed variance-band badge (Phase 3), Applied % auto-shown for percentage-type elements.
2. **EAC formula** — confirmed: single formula, `BAC / CPI`, no per-element picker.
3. **Reassessment log generalisation** — confirmed: generalise now rather than copy a third time. Phase 7 becomes: extract one shared backend service (parametrised by parent table/FK/entity name) and one shared frontend component (parametrised by API path + trigger fields + display strings), then re-point Risk and ICD at the shared implementation alongside adding Cost.
4. **GFA/Space count** — confirmed: project-level, and **explicitly optional/nullable** — not every project will have a meaningful GFA (e.g. non-building projects), so £/m² and £/Space unit-rate figures should simply not render when GFA/space count aren't set, rather than forcing every project to populate them.

---

**Status:** Approved — proceeding phase by phase, TaskCreate-tracked, verified at each step — same process as Risk and ICD.
