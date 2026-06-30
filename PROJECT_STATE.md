# ProsotaPMO — Project State

**Last updated:** 2026-06-30
**Updated by:** Claude (Anthropic), prototype-phase session
**Status:** Prototype complete. Production build not yet started.

> **Instructions for whoever reads this next (human or Claude):** This file is the single source of truth for where ProsotaPMO stands. Read it fully before writing any code. Update it at the end of every working session — what changed, what's next, what's blocked. Treat stale entries as a bug in the project, not just the document.

---

## 1. What This Project Is

ProsotaPMO is a browser-native, AI-powered, sector-agnostic project management platform for organisations running structured PMOs — schedule, cost, risk, and change control in one integrated tool. Built by founder Maro Sota (Louis Oghenemaro Sota, Senior Planner / 4D Project Controls Specialist, Prosota Consulting Ltd) in direct collaboration with Claude as the engineering partner.

Full business rationale: see `docs/business-case.docx` (not yet copied into repo — pull from prior session output).
Full prototype scope: see `docs/project-scope.docx` (not yet copied into repo — pull from prior session output).

## 2. Current State (As of This Handoff)

**A complete, fully-interactive HTML/CSS/JS prototype exists.** Single file: `prosota-pmo.html` (~6,400 lines, ~575KB). No backend, no database, no persistence, no real file parsing. Every UI interaction works; all data is hard-coded/in-memory and resets on reload.

**This prototype is the product specification, not a codebase to lift into production.** Production engineering should treat its behaviour as the authoritative UX spec and rebuild cleanly in the target stack (Section 5).

### What's fully designed and demonstrated in the prototype:

- 9 views: Project Selector, Controls Dashboard (3 tabs), Scheduling, Risk Register, Cost Plan, ICD Tracker, File Manager, Period Manager, Export Center
- A cross-module linking graph (Activities ↔ Risks ↔ Cost Elements ↔ Issues/Changes/Decisions) with typed relationships (causes/impacts/mitigates/relates_to)
- 4 AI capabilities: context-aware co-pilot, causally-aware baseline narrative, Setup Assistant (suggestion inbox), Generative Visual Assistant (chart-on-request)
- Period governance workflow (Live → Frozen → Amendment → Incorporated)
- Import/export UX for XER/MPP/Asta PP/XML/XLSX (UI only, no real parsing)
- Print/Preview framework per module
- Global Export Center (Excel/Power BI star-schema export, PPTX/PDF report builder)

**Nothing in production has been started.** No repo exists yet beyond this handoff. No infrastructure is provisioned. No backend code has been written.

## 3. Immediate Next Steps (Sprint 1, Week 1–2 per business case)

In priority order:

1. [x] Initialise this repo properly: `backend/`, `frontend/`, `docs/`, `infra/` folder structure (see Section 6)
2. [x] Copy `prosota-pmo.html`, the business case docx, and the project scope docx into `docs/prototype/` for reference
3. [ ] Stand up AWS infrastructure skeleton (ECS Fargate, RDS Aurora Postgres, S3, CloudFront) — see business case Section 6.2 for budget constraints (~£24k/yr infra at Phase 1 scale)
4. [x] FastAPI project scaffold with the 5-table core schema (Section 4 below) and Alembic migrations
5. [ ] Auth0 integration for SSO/MFA
6. [x] CI/CD pipeline (GitHub Actions): lint, test, deploy to staging on merge to `main`

Do NOT start frontend work until the core API for at least Activities + Risks exists and is tested — the linking graph (Section 4.3) needs both sides to exist before it's meaningful to build against.

## 4. Core Data Model (Authoritative — Carry Forward From Prototype)

This is the schema the prototype's Export Center already demonstrates as a star-schema; use it as the real Postgres schema, not just an export format.

### 4.1 Core Entities

| Table | Key Fields | Notes |
|---|---|---|
| `organisations` | id, name, plan_tier | Multi-tenancy root |
| `projects` | id, org_id (FK), name, client_name, status | |
| `periods` | id, project_id (FK), period_label, start_date, end_date, cutoff_date, freeze_status (live/frozen/incorporating), baseline_locked_flag | Drives the whole Period Manager state machine |
| `activities` | id, project_id, period_id, task_name, wbs_path, start, finish, bl_start, bl_finish, variance_days, pct_complete, total_float, is_critical | fact_schedule in prototype's export schema |
| `risks` | id, project_id, period_id, title, category, status, probability, impact, rating, emv_cost, emv_schedule_days, mitigation_status | fact_risk |
| `cost_elements` | id, project_id, period_id, element_group, description, budget, forecast, actuals, variance, cpi, spi, rev_a_baseline, cost_per_m2 | fact_cost |
| `icd_items` | id, project_id, period_id, item_type (issue/change/decision), status, priority, owner, cost_impact, schedule_impact_days, raised_date, closed_date | fact_icd |

### 4.2 Period Baselines

Each `periods` row, once frozen, must produce an **immutable snapshot** of all linked activities/risks/cost_elements/icd_items at that point in time — this is what the Baseline Comparison Engine compares against. Do not let frozen-period data be editable; this is a core trust guarantee of the product, not an implementation detail.

### 4.3 Cross-Module Linking (Critical — This Is a Genuine Differentiator)

```sql
CREATE TABLE record_links (
  id UUID PRIMARY KEY,
  source_type VARCHAR NOT NULL,  -- 'activity' | 'risk' | 'cost_element' | 'issue' | 'change' | 'decision'
  source_id UUID NOT NULL,
  target_type VARCHAR NOT NULL,
  target_id UUID NOT NULL,
  link_type VARCHAR NOT NULL,    -- 'causes' | 'impacts' | 'mitigates' | 'relates_to'
  note TEXT,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT now()
);
```

This single table is what powers the prototype's "Linked" tab on every record type, and the causal-chain-tracing AI narrative (Section 5.2 of the business case / Section 5 of the scope doc). Do not normalise this into separate join tables per type pair — the graph-edge shape is deliberate and was chosen specifically to support arbitrary many-to-many relationships across all 6 record types without schema changes.

## 5. AI Integration — What Must Be Rebuilt Faithfully

The prototype's AI features are not decorative; they are the product's primary differentiator per the business case. Four distinct capabilities, each with its own trust model — **do not collapse these into one generic "AI chat" feature**:

1. **Context-aware co-pilot** — system prompt is built dynamically per active module/record, enriched with the 3 most relevant causal chains from `record_links`. Always-on side panel.
2. **Causally-aware baseline narrative** — on-demand (user clicks "AI Summary"), traces `record_links` up to 4 hops from changed records since the comparison baseline, feeds traced chains + raw metric deltas into the prompt, generates a 3-paragraph root-cause narrative. **The traced chains themselves are never shown in the UI** — this was tried and removed after user testing found it cluttered; the AI's written narrative is the only surface for this reasoning.
3. **Setup Assistant** — fires once per import event, proposes new risks/cost elements/links from a fixed, ranked rule set (max 5 suggestions per trigger). **Never auto-writes** — every suggestion requires explicit Accept/Edit/Dismiss. In production this needs a real rule engine reading the actual imported file's content, not the prototype's hard-coded pattern matches.
4. **Generative Visual Assistant** — intent-matches a free-text request to one of a **fixed, whitelisted set of real data queries** against the fact tables. **This is not free-form chart generation** — there is no path for the AI to invent a number. If a query doesn't match a known intent, it says so and asks for specificity. Production should expand the intent library but preserve this constraint absolutely; it's a deliberate safety/trust design, not a limitation to "fix" by going fully generative.

## 6. Recommended Repo Structure

```
prosota-pmo/
├── PROJECT_STATE.md          <- this file, update every session
├── ARCHITECTURE.md           <- technical architecture decisions (companion doc)
├── docs/
│   ├── business-case.docx
│   ├── project-scope.docx
│   └── prototype/
│       └── prosota-pmo.html  <- reference UX spec, do not deploy this file
├── backend/
│   ├── app/
│   │   ├── models/           <- SQLAlchemy models per Section 4 schema
│   │   ├── api/               <- FastAPI routers per module
│   │   ├── services/          <- business logic, incl. causal chain traversal
│   │   └── ai/                 <- the 4 AI capability modules, kept separate
│   ├── alembic/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── modules/           <- one folder per prototype view
│   │   ├── components/
│   │   └── lib/
│   └── tests/
└── infra/
    └── terraform/
```

## 7. Things Explicitly Out of Scope (Don't Accidentally Build These)

- BIM/IFC/4D simulation — deliberate positioning decision, platform is horizontal/sector-agnostic
- Mobile-responsive layout in Phase 1 — desktop-first per business case
- Second project tenant beyond the seed data — single real project, multi-tenant *architecture* yes, but don't over-invest in demo data variety early
- Free-form/generative chart creation — see Section 5.4 above, this is intentional

## 8. Key People & Roles

| Role | Who | Notes |
|---|---|---|
| Founder, Product, Domain Expert, Sales | Maro Sota | Makes all product/commercial decisions |
| Engineering | Claude (via Claude Code from this point forward) | Executes all code; this chat interface is no longer where engineering happens |

## 9. Session Log

| Date | What Happened | Next Session Should... |
|---|---|---|
| 2026-06-30 | Prototype completed end-to-end across an extended chat session. Business case (v3) and Project Scope document finalised. This handoff doc created to bridge into Claude Code / production build. | Set up the actual repo, copy reference docs in, and start Sprint 1 infra work per Section 3. |
| 2026-06-30 | Sprint 1 tasks 1, 2, 4 complete. Repo scaffolded, docs in place, FastAPI + all 9 SQLAlchemy models + Alembic initial migration done. API confirmed running locally at http://localhost:8000 with Postgres 16 (native Windows install). psycopg3 used as driver (asyncpg dropped — no Python 3.14 wheels). Docker Hub unreachable from dev machine — Docker Compose file exists but is not the active local dev path. | Next: decide between task 5 (Auth0) or task 6 (CI/CD), or move to first real API endpoints (Activities + Risks CRUD) to unblock frontend work. |
| 2026-06-30 | Sprint 1 tasks 4 + 6 fully complete. Full CRUD + tests for Activities, Risks, Cost Elements, ICD Items, and record_links (bidirectional graph). Cost elements: fixed/percentage dual-type with live computed values. ICD items: single-table discriminator (issue/change/decision) with type-field validation. GitHub Actions CI live — PostgreSQL 16 service container, pytest on push/PR. All pushed to GitHub (eng-lou/Prosota-PMO). Tasks 3 (AWS) and 5 (Auth0) still deferred. | Next: Auth0 integration (task 5) or AWS infra skeleton (task 3). Backend API is complete enough to unblock both. Frontend remains blocked until Auth0 exists. |
| 2026-07-01 | Auth0 JWT integration complete (task 5). Frontend scaffold live: React 18 + TypeScript + Tailwind + React Query + Vite. Auth0 SPA login working end-to-end. Project selector screen live — fetches real projects from API, creates new ones, persists selection to sessionStorage. Shell layout with sidebar nav (all 8 modules including File Manager). CORS configured. Auto-provisioning on first login (get_db_user creates org + user if not found). Projects, Periods, Users/me endpoints added to backend with tests. | Next: build the module views one at a time — Risk Register first (most core to the differentiator), then Cost Plan, then the others. Also need to run pytest after today's backend additions and commit everything. |

---

**If you are Claude reading this at the start of a new Claude Code session:** read this file, then `ARCHITECTURE.md`, then check `git log` for what's actually been committed (this file may lag behind reality if a session forgot to update it — trust the commit history over stale prose). Update Section 9 before you finish your session, even if the session was short.
