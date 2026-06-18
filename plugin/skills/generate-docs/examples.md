# generate-docs — worked example

Projecting the **whole** spec tree into the project's doc-site — every area, organized by the **four documentation modes** rather than mirroring the spec folders.

> **Claude:** The spec sections feed the modes, they don't define the top-level shape. Every area is covered (discovery → delivery), so the site is the complete project documentation. Each section is tagged by its mode; releases are tagged, so the root carries a version selector. API contracts exist → the API reference folds in under `api/`. Module internals were designed **per-slice**, so the scattered `07-solution/impl/*` files + the per-task `design:` decisions are consolidated into one **Implementation design** section, grouped by module — read as a document, not per-task fragments.

Doc-site outline written to `docs-site/` (regenerated wholesale — pure projection, mints no IDs):

- **Tutorial** (learning-oriented) — `tutorial/`
  - Getting started: book your first repair end-to-end (the one required starter path)
- **How-to** (task-oriented) — `how-to/`
  - Reschedule a job · Issue a refund · Add a branch · Wire up webhooks · Operate an incident (from the runbooks)
- **Reference** (information-oriented)
  - All requirements: use-cases (UC-/AC-), NFRs (NFR-/ASR-), data (DATA-), security (SEC-), obligations (OBL-), design-system (DS-), ML (ML-)
  - The API / event reference (API-/EVT-) → `api/` · the data classes
  - Traceability matrix · Glossary
- **Explanation** (understanding-oriented) — the full narrative spec
  - Overview: vision / goals / north-star · market & positioning
  - Constraints & stakeholders · System context (boundary + C4 L1)
  - Domain model: context-map · aggregates · events (Mermaid)
  - Solution architecture: style · C4 · stack · **module map & seam contracts** · key sequences — plus data / security / infra / observability / test / **ML** architecture
  - **Implementation design** — consolidated from the per-module `07-solution/impl/*` internals + the per-task `design:` decisions, grouped by module / subsystem
  - Commercial model & growth · ADRs · key decisions
- Plus: readiness dashboards
- `index.html` — navigable root, sections cross-linked by stable ID, each tagged by mode, **version selector** (v1.0 / v1.1)
- `assets/` — Tailwind + Mermaid via CDN (self-contained)

(no spec changes — read-only projection of the whole `spec/` tree. Wired in CI: a push to `main` touching the spec rebuilds `docs-site/` and Pages deploys it.)
