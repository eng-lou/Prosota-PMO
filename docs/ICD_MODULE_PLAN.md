# ICD Tracker Module — Consolidated Plan

**Purpose:** Same exercise as `docs/RISK_MODULE_PLAN.md`, applied to ICD Tracker (Issues, Changes, Decisions) — reconcile what the prototype/scope docs already specified, what PMBOK7/Rita Mulcahy best practice adds, and what's actually built today, before continuing. Read the prototype's full ICD Tracker markup (6 KPI cards, 3 sub-tabs, a 6-tab type-adaptive detail panel) and the relevant reference chapters (Ch. 4 "Perform Integrated Change Control", the Issue Log artifact in Ch. 6) directly this session, not from memory.

Applying the process learned from the Risk Module: this doc is for review first — nothing implemented yet. Open questions are at the end.

---

## A. What the Prototype + Scope Document Already Specified

Source: scope doc Section 4.6, prototype markup (`view-tracker`, lines ~4201–4749).

### A.1 KPI strip (lives on the ICD Tracker page itself, not the Dashboard)
6 cards, explicitly paired by domain: Open Issues / Overdue Issues, Changes Pending / Changes Approved (with net £/days impact), Decisions Pending / Decisions Made.

### A.2 Three sub-tabs, each its own table with *different columns per type*
- **Issues**: ID, Title, Category, Priority, Status, Owner, **Due Date**, Linked To
- **Changes**: CR#, Title, **Type** (Variation / Client Instruction / Omission), **Cost Impact (signed, +/-)**, Sched Impact, **Raised By**, Status, Date — plus a **"Net Approved Change Impact"** summary row (sums approved changes only)
- **Decisions**: DEC#, Decision Required, Category, Decision Maker, Status, Required By, **"If Late"** (consequence text — what happens if the decision slips)

### A.3 Type-adaptive Detail panel — 6 tabs
1. **General** (3-column layout) — Item Details (ID, Title, Type, Category, Priority, Status) | Ownership & Dates (**Owner, Raised By, Date Raised, Due Date, Date Closed**, Linked To) | Description & Action (**Description** textarea, **Action Taken / Resolution** textarea)
2. **Impact & Links** — Programme Impact (Schedule Impact *rating* High/Med/Low/None + Days at Risk, Cost Impact *rating* + Est. Cost, **Quality Impact rating**, a Critical Path Impact callout) | a compact linked-records preview | **Contract & Change Reference** (Triggers CR? Yes/No/TBC, CR Status, Cost Claim, EOT Claim, a free-text contract clause reference e.g. "NEC3 ECC Clause 60.1(12)")
3. **Actions & Comments** — an Action Items sub-list (own `ACT-01` codes, owner, due date, status, progress bar — identical shape to Risk's Mitigation Actions) **plus** a threaded Comments discussion (avatar, name, timestamp, message)
4. **History & Audit** — a fully *automatic*, system-generated timestamped trail (status changes, comments added, links created) — distinct from Risk's user-prompted reassessment log
5. **Notifications** — Watchers & Assignees (role: Owner/Assigned/Watcher) + per-event notification preferences (email/in-app toggles per event type)
6. **Linked** — cross-module linking (already built, generalised)

### A.4 Import/Export/Print
Same pattern as Risk/Cost: Excel (.xlsx) and ICD XML (.xml) import/export, Print/Preview.

---

## B. What PMBOK7 / Rita Mulcahy Add

Read directly this session: Ch. 4 "Perform Integrated Change Control" (Rita Mulcahy, full section) and the Issue Log artifact description (Ch. 6); PMBOK7 glossary entries for Change Log and Issue Log.

### B.1 Issue Log — canonical field structure (Ch. 6, Figure 6.7)
> "Issue # | Issue | Date Added | **Raised By** | Person Assigned | **Resolution Due Date** | Status | Date Resolved | **Resolution**"

Confirms three concrete gaps versus our current `icd_items` fields: no **raised_by** (who raised it — distinct from `owner`, who resolves it), no **resolution due date**, no **resolution** text (what the outcome actually was, not just the status).

Also: **"issue" is defined as "a current condition or situation that may have an impact on project objectives"** — distinct from a Risk (an uncertain *future* event). This is why issues correctly have no `probability` field in our schema — that part is already right.

### B.2 Perform Integrated Change Control — the real discipline behind "Changes"
- **Impact must be assessed across all constraints** — scope, quality, risk, resources, cost, schedule, customer satisfaction — not just cost/schedule. Our current `cost_impact`/`schedule_impact_days` on changes only cover two of these. The prototype's Impact & Links tab already models this better (Schedule/Cost/**Quality** impact ratings) — worth matching.
- **Change Control Board (CCB)**: changes affecting baselines/charter need CCB or sponsor approval; smaller changes can be PM-approved directly. Implies a change needs an **approval decision** (approved/rejected/deferred) distinct from its generic lifecycle `status`, and **if rejected, the reason must be documented**.
- **Change Log**: "a comprehensive list of changes submitted and their **current status**" (PMBOK7 glossary) — we already have this as the Changes sub-tab; the gap is the *type* of change (Variation/Client Instruction/Omission — all real NEC/JCT terms) and the CCB decision fields.
- Changes should be traceable to what triggered them (an issue, a risk) — already covered by `record_links`, no gap.

### B.3 Decision Log — not a formal PMI artifact, but standard PMO practice
Neither Rita Mulcahy nor PMBOK7 name a "Decision Log" as an official artifact (decisions are handled via CCB/meeting minutes in PMI's model). However this is universal real-world practice (RAID logs), and matches Maro's own NEC/JCT domain expertise directly — treated as a founder product decision already made (Decisions already exist as a peer to Issues/Changes in our schema), not something requiring textbook validation. The prototype's "If Late" consequence field is a good, concrete addition worth adopting.

### B.4 What's *not* worth chasing from the reference material here
Notification preferences, watcher lists, and audit-trail automation are implementation/tooling concerns, not PM-methodology concepts — the reference books have nothing further to add on these; they're addressed as build/scope questions in Section D instead.

---

## C. Gap Analysis

| Capability | Prototype/Scope | PMBOK/Rita Mulcahy | Currently built? |
|---|---|---|---|
| Basic CRUD, type discriminator, per-type validation | Yes | — | ✅ Yes |
| Human-readable reference codes (ISS-/CHA-/DEC-) | Yes | — | ✅ Yes |
| Cross-module linking | Yes | (implicit) | ✅ Yes, generalised |
| Per-type status dropdown | Yes | Yes ("current status") | ✅ Yes (fixed earlier this session) |
| `title` field | Yes | Yes | ✅ Yes (fixed earlier this session) |
| **`description`** (separate from title) | Yes | (implicit) | ❌ Missing — only a short `title` exists |
| **`raised_by`** (who raised it, vs `owner` who resolves it) | Yes | Yes — explicit in Issue Log structure | ❌ Missing |
| **`due_date`** (issues) / **Resolution Due Date** | Yes | Yes — explicit in Issue Log structure | ❌ Missing (only `raised_date`/`closed_date` exist) |
| **`resolution`** / Action Taken text | Yes | Yes — explicit in Issue Log structure | ❌ Missing |
| Change **type** (Variation/Client Instruction/Omission) | Yes | (NEC/JCT real-world terms) | ❌ Missing |
| Change **CCB decision** (approved/rejected/deferred) + rejection reason | Implied by status | Yes — explicit | ❌ Missing — only generic `status` |
| Contract/change reference (clause, CR status, cost claim, EOT claim) | Yes | (NEC/JCT specific, not PMI-generic) | ❌ Missing |
| Decision **"If Late"** consequence field | Yes | (not formal PMI, but sound practice) | ❌ Missing |
| Impact assessed across scope/quality/risk/cost/schedule (not just cost/schedule) | Yes (Quality Impact rating) | Yes — explicit | ❌ Missing — only cost/schedule |
| Action Items sub-list (own codes, owner, due, status, progress) | Yes | (implicit) | ❌ Missing — reuse the pattern already built for Risk Mitigation Actions |
| Comments/discussion thread | Yes | — | ❌ Missing (new concept, not built anywhere yet) |
| Automatic History & Audit trail | Yes | — | ❌ Missing (Risk's reassessment log is user-*prompted*, not automatic — different mechanism) |
| Notifications (watchers, preferences) | Yes | — | ❌ Missing — needs real notification infrastructure (email/in-app) that doesn't exist anywhere in this app |
| KPI strip on the tracker page | Yes | — | ❌ Missing — but cheap (pure aggregation over already-loaded data, same pattern as Risk's group-by) |
| Search/Filters/Group toolbar | Yes | — | ❌ Missing — same pattern already built for Risk, should generalise |
| Export/Print | Yes | — | ❌ Missing — same pattern already built for Risk, should generalise |
| Import (real XER/XLSX/XML parsing) | Yes (prototype UI only) | — | ❌ Deliberately deferred, same as Risk |

---

## D. Proposed Phased Plan (for review — nothing implemented yet)

**Phase 1 — Fill the Issue Log gaps** (small, matches the book's own field structure exactly)
- Add `description` (Text, all types), `raised_by`, `due_date`, `resolution` (Text) to all ICD items

**Phase 2 — Change-specific fields (the real Integrated Change Control gap)**
- Add `change_type` (Variation / Client Instruction / Omission), `ccb_decision` (approved/rejected/deferred, distinct from generic `status`), `rejection_reason`
- Add `contract_reference` (free text — clause references), `cost_claim`, `eot_claim` (extension-of-time claim, in days)
- Add Quality Impact alongside existing cost/schedule impact — a rating (High/Med/Low/None), matching the prototype exactly, not a new quantitative field

**Phase 3 — Decision-specific field**
- Add `if_late_consequence` (Text) to decisions

**Phase 4 — Action Items sub-list**
- New `icd_action_items` table — same shape as `risk_mitigation_actions` (own `ACT-01` per-item codes, owner, due date, status, % complete). Reuse the pattern, don't reinvent it.

**Phase 5 — Comments**
- New `icd_comments` table (item_id, author = the real authenticated user via Auth0, body, created_at). Genuinely buildable now since real user identity already exists in this app (unlike Notifications, which needs infrastructure that doesn't exist).

**Phase 6 — KPI strip + Search/Filters/Group/Export/Print**
- KPI strip: pure client-side aggregation over the already-loaded items list (Open/Overdue Issues, Pending/Approved Changes + net impact, Pending/Made Decisions) — same complexity as Risk's group-by counts, no new endpoints.
- Generalise the Search/Filters/Group/Export/Print components already built for Risk (`RiskRegister.tsx`'s toolbar, `exportRisks.ts`, `RiskPrintView.tsx`) rather than rewriting from scratch.

**Phase 7 — History & Audit, reusing Risk's pattern (decided, not automatic)**
- Maro's decision: reuse the `risk_reassessments` user-prompted pattern rather than building automatic field-diff logging. New `icd_reassessments` table (item_id, note, reviewed_at), `IcdForm` auto-detects trigger-field changes (status, priority for issues, ccb_decision for changes, etc.) and prompts for an optional note — same mechanism as Risk, not generalised into shared code yet (second use of the pattern; worth generalising on a third).

**Explicitly still deferred, with reasoning (matches how Import was reasoned about for Risk):**
- **Notifications (watchers, email/in-app preferences)** — would need real notification infrastructure (an email service, an in-app notification system) that doesn't exist anywhere in ProsotaPMO yet. Building the settings UI without real sending would be the exact "looks like it works but doesn't" mistake this whole session has been fixing.
- **Import** — same reasoning as Risk: real file parsing + field-mapping UI is a bigger, separate task.

---

**Decisions confirmed by Maro (2026-07-01):** reuse Risk's user-prompted reassessment pattern for History & Audit (not automatic diffing); analysis and phased approach approved as written. Proceeding phase by phase, TaskCreate-tracked, verified at each step — same process as the Risk Module.
