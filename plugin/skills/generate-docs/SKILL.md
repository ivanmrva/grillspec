---
name: generate-docs
description: >-
  Generate the project's documentation — a self-contained static HTML doc-site that assembles the **full spec** (every area, discovery → delivery) plus the **implementation design** consolidated from the per-module/per-task designs — overview, domain, requirements, architecture, implementation, ADRs, traceability, glossary, dashboards. Re-runnable and CI-friendly. Loads the shared exec core.
disable-model-invocation: true
argument-hint: the spec to generate a docs site from
---

# generate-docs

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **project a static HTML doc-site from the spec tree**.

## Process
1. **Organize by the four documentation modes, not just the spec tree** — a learning-oriented **tutorial**, task-oriented **how-to guides**, **reference**, and **explanation** (the spec sections feed these, they don't define the top-level shape). Ship at least a **getting-started tutorial** plus the **key how-tos**, alongside the projected reference/explanation content.
2. **Build the site** — a navigable static site, self-contained via CDN (Tailwind, Mermaid), cross-linked by stable ID, covering the sections in the Output tree; **tag each generated section by its mode** (tutorial / how-to / reference / explanation).
3. **Versioned docs** — when releases are tagged, expose a **per-release/version selector** so a reader can read the docs for the version they run.
4. **Fold in the API reference** — if the project exposes an API (`API-`/`EVT-` contracts exist), generate the API reference and embed it as a section under `api/` so the project docs and the API reference ship as one navigable bundle, cross-linked by ID. No API surface → skip it.
5. **Assemble the full spec + consolidate the implementation design** — cover *every* area so the site is the complete project documentation (discovery · product · constraints & stakeholders · system context · domain · all requirements incl. ML · the solution: architecture, data, API, security, infra, observability, test & ML architecture · commercial/growth · delivery). Because module internals are designed **per-slice**, gather the scattered per-module designs (`07-solution/impl/*`) + the per-task `design:` decisions into one coherent **implementation-design** section grouped by module/subsystem — the realized design read as a document, not per-task fragments.

## Rules
- **Regenerate wholesale** (the one exception to reconcile-don't-regenerate) — the site is a pure projection of the spec into HTML: it mints no IDs and stores no decisions, so rebuilding from scratch each run is correct and keeps it honest. Timeless voice, for a reader who was never in the room.
- **project, don't author** — a tutorial or how-to is *assembled and sequenced* from material already in the spec (use-cases, journeys, runbooks, operations records), never net-new narrative, steps, or decisions untraceable to the spec; a needed guide with no source is a **doc-gap to surface**, not prose to invent
- **CI wiring (the intended use)** — deterministic and runnable headless, so it slots into the spec/doc-governance workflow (separate from the app's infrastructure pipeline): on every push to `main` that touches the spec, build then commit `docs-site/`, and `.github/workflows/docs-site.yml` deploys it to GitHub Pages (enable Pages once; `workflow_dispatch` triggers it manually). For hands-off docs, run this headless in CI on spec changes via a Claude GitHub Action (needs `ANTHROPIC_API_KEY`).

## Output
Written under `docs-site/` (repo-root, non-spec zone; regenerated wholesale from spec/; CI deploys to Pages):

| File / target | Captures | Format |
|---|---|---|
| `index.html` | navigable site root — sections cross-linked by stable ID, each **tagged by mode** (tutorial/how-to/reference/explanation); **version selector** when releases are tagged | — |
| `tutorial/` | learning-oriented getting-started tutorial | — |
| `how-to/` | task-oriented how-to guides | — |
| `assets/` | CSS/JS (self-contained via CDN: Tailwind + Mermaid) | — |
| `api/` | the embedded API reference (only when API-/EVT- contracts exist) | — |

content inside the site, mapped to modes — **tutorial**: getting-started · **how-to**: key task & operations guides (from the runbooks/operations records) · **reference**: all requirements (UC-/AC-, NFR-/ASR-, DATA-, SEC-, OBL-, DS-, ML-) · the API/event reference (API-/EVT-) · the data classes · the traceability matrix · the glossary · **explanation** (the full narrative spec): vision/goals/north-star · market & positioning · constraints & stakeholders · the system context (boundary + C4 L1) · the domain model (context-map · aggregates · events) · the **solution architecture** (style · C4 · stack · **module map & seam contracts** · key sequences) + data / API / security / infra / observability / test & **ML** architecture · the **implementation design** (per-module internals + per-task design, assembled per module/subsystem) · the commercial model & growth · the ADRs & decisions log; plus readiness dashboards
(no spec changes — pure projection of spec/)
Consumes: the whole `spec/` tree + `08-delivery/verification/traceability.md` + the `adr/` ADRs — read-only, never edits the spec.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
