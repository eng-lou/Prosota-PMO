# ProsotaPMO — Architecture

**Companion to `PROJECT_STATE.md`.** This file covers *how* things should be built; `PROJECT_STATE.md` covers *what exists right now and what's next*. Update this file when an architectural decision is made or changed — not for routine feature work.

---

## 1. Stack (Decided — From Business Case, Not Up For Casual Revisiting)

| Layer | Technology | Why |
|---|---|---|
| Frontend | React 18 + TypeScript, TailwindCSS, Recharts, React Query, Vite | Direct migration path from prototype's component structure; strong AI-assisted dev velocity |
| Backend API | FastAPI (Python) + SQLAlchemy + Alembic | Async performance; Python AI/ML ecosystem; clean OpenAPI generation |
| Database | PostgreSQL (primary), Redis (cache/sessions), S3-compatible (files) | ACID; row-level security for multi-tenancy; proven at scale |
| AI/ML | Anthropic Claude API, custom context-injection layer | Proven in prototype; model-agnostic design (don't hard-couple to one model) |
| Infra | AWS — ECS Fargate, RDS Aurora, ElastiCache, S3, CloudFront | ISO 27001-aligned; UK data residency available; managed services suit solo/small-team ops |
| Auth | Auth0 — SSO, MFA, SAML | Enterprise-ready without custom auth code |
| Mobile | Progressive Web App (Phase 1), React Native (Phase 2) | PWA gives immediate access; native app deferred |

**Do not introduce a different frontend framework, ORM, or cloud provider without updating this file and explaining why** — these were deliberate choices tied to team size (founder + AI), budget (see business case Section 6), and development velocity, not arbitrary defaults.

## 2. Multi-Tenancy

Organisation-level data isolation via row-level security in Postgres, not separate databases per tenant. Every table from Section 4 of `PROJECT_STATE.md` carries (directly or via FK chain) an `org_id`. Tenant-scoped API keys for any external integrations.

## 3. The Period State Machine — Must Be Server-Authoritative

The prototype implements period state (`live` / `frozen` / `incorporating`) as client-side JavaScript state. **This must move server-side in production.** The freeze action is a trust-critical operation — once a period is frozen, the API must reject any write to that period's activities/risks/cost_elements/icd_items at the database layer, not just hide the edit UI. Treat "can frozen data be edited" as a security property, not a UX property.

Recommended approach: a `period_id` foreign key on every mutable record, plus a Postgres trigger or application-layer check that rejects writes where `periods.freeze_status != 'live'` for that record's period, unless the write is explicitly tagged as a Week 4 "amendment" (which itself should be a separate, append-only `amendments` table — never an in-place edit to frozen data).

## 4. The Causal Chain Engine — Algorithm to Preserve

The prototype's `findCausalChains()` function (JavaScript, in-memory graph traversal) should be reimplemented server-side, likely as:

- A recursive CTE in Postgres for simple cases, or
- A dedicated graph traversal in the FastAPI service layer if chain logic grows more complex than SQL comfortably expresses

Behaviour to preserve exactly:
- Traverse up to 4 hops from any changed node
- Rank by chain length (longer cross-module chains = higher priority)
- De-duplicate chains that contain the same node set
- Cap results (prototype caps at 5) before they're fed into any AI prompt — this is a cost control as much as a UX one

## 5. AI Prompt Architecture

Keep the 4 AI capabilities (Section 5 of `PROJECT_STATE.md`) as **separate prompt-construction functions/services**, even if they share an underlying Claude API client. Do not build one generic "ask the AI anything" endpoint that all four features call through with different system prompts bolted on — the trust models differ too much (the Generative Visual Assistant's hard intent-whitelisting in particular must not leak into the more open-ended co-pilot, and vice versa).

Each AI service should log: the prompt sent, the data injected (causal chains, fact-table rows, etc.), and the response — for auditability and for debugging when the narrative seems wrong. This is a PMO tool used for things like NEC/JCT change control; "the AI said X and we can't show our working" is not acceptable in this domain.

## 6. Import/Export — Real Parsing Requirements

The prototype's import wizards (XER, MPP, Asta PP, XML) are UI-only. Production needs real parsers:

- **XER (Primavera P6)**: tab-delimited format, well-documented; the founder has existing familiarity with `xerparser` (Python) per prior session history — reuse rather than rebuild
- **MPP (Microsoft Project)**: binary format, no good pure-Python parser exists; likely needs either a licensed library or a conversion-via-MS-Project-API approach — flag this as a research spike before committing engineering time
- **Asta PP**: proprietary; lowest priority of the four, confirm actual customer demand before investing here
- **XML**: most tractable — Project XML is a documented schema

Field-mapping UI (Step 2 of the prototype's import wizard) should be config-driven per format, not hard-coded per format — new formats should be addable by adding a mapping config, not writing new UI.

## 7. Testing Strategy

- Backend: pytest, target 80% coverage generally, 100% on: period freeze/unfreeze logic, the linking graph CRUD, and any AI prompt-construction function (test the *data going into* the prompt, not the AI's output)
- Frontend: component tests for each module; one end-to-end test per critical workflow (import a schedule → see Setup Assistant suggestions → accept one → see it linked)
- Never skip testing the period freeze boundary — this is the feature most likely to have a subtle bug with real financial/legal consequences for users (NEC/JCT change control relies on accurate frozen baselines)

## 8. What NOT to Do

- Don't add BIM/IFC support "since it would be easy" — this is a considered positioning decision (`PROJECT_STATE.md` Section 7), not an oversight
- Don't let the Generative Visual Assistant become free-form/generative — the whitelisted-intent design is a deliberate trust boundary
- Don't normalise `record_links` into per-type-pair join tables — the graph-edge shape is intentional
- Don't build a single "AI chat" endpoint shared by all 4 AI features — keep them architecturally separate (Section 5)
- Don't let frozen period data be client-side-only protected — must be enforced server-side (Section 3)

---

**Update history:** this file created 2026-06-30 alongside `PROJECT_STATE.md`, at the handoff from prototype-phase chat session into Claude Code production development.
