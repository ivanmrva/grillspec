---
name: derive-tasks
description: >-
  Break a spec into minimal, vertically-sliced, build-ready tasks for a coding agent — each a complete reference manifest, phase-tagged and dependency-ordered, walking-skeleton first. Use when you need the spec turned into build-ready slices. Loads the shared derive core.
disable-model-invocation: true
argument-hint: a spec, design docs, or a feature to break into tasks
---

# derive-tasks

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **task breakdown** — turning a recorded spec into minimal, vertically-sliced, build-ready tasks. A task is rarely one-shot: derive → ask → iterate until each is implementation-final (zero ambiguity), producing slice-specific detail (incl. UX mockups/microcopy) the global spec doesn't cover.

## Method
1. **Start with the walking skeleton.** The first task wires the architecture end-to-end, scaffolds the repo, stands up governance (below), wires the design-token pipeline when there's a UI, **deploys to a dev environment with a smoke test + an automated rollback** (the release path is part of the end-to-end wiring), emits the human-prerequisites bootstrap checklist, and seeds the Tier-B system/journey acceptance tests + architecture fitness functions as pending — so they exist before any feature code.
2. **Slice vertically.** Cut the first MVP use-case into a tracer bullet: a narrow but COMPLETE path through every layer (schema → domain → api → ui → tests), demoable on its own. Never a horizontal slice of one layer; right-size to one agent session.
3. **Fill every dimension by reference.** For each slice, each applicable dimension (behavior, domain, data, api, ux, a11y, security, nfr, integration, placement, **design**, tests, dependencies, DoD) is exactly one of: a spec-ID reference, `N/A — why`, or `GAP <what's missing> — UNRESOLVED`. The **ux** dimension references the slice's **clickable prototype screen** (the exact visual + interaction reference to build against); the **a11y** dimension names the keyboard path · focus order · contrast · the relevant current-WCAG success criteria (default `N/A — headless` for a non-UI slice); the **design** dimension is `inline` for a simple/CRUD slice (the agent designs as it TDDs) or **`design-first`** for a complex slice (hard algorithm · real concurrency · cross-context saga → its module internals are designed & reviewed before coding).
4. **Force every gap to a resolution.** An UNRESOLVED gap forces one conscious choice: complete it now (elicit just-in-time → it lands in the source spec), mark `N/A — why`, or accept a default (write an ADR, reference it). For a UX/decision gap, produce a concrete default for the user to ratify, don't author blind.
5. **Tag, order, finalize.** Tag each task's phase (MVP/near/deferred) and dependencies; set its `afk:` marker. Order = topological sort, MVP-first → `build-order.md`. Apply the **acceptance gate**: each slice is independently **valuable / demoable** (delivers a user-visible outcome on its own, not a horizontal layer); record that outcome in the manifest. Implementation-final only when no dimension is an UNRESOLVED gap and the gate holds.
6. **Iterate** — derive the manifest, detect unresolved dimensions (especially slice-specific UX), ask or produce, until an agent could implement with zero ambiguity.

## Rules
- **Minimal & vertical** — the smallest independently-testable end-to-end slice; never horizontal layers, never big-bang; right-size to one agent session
- **Walking-skeleton first** — it stands up two path-scoped governance workflows: (a) **code governance** — pre-commit hooks + the app CI/CD pipeline as GitHub Actions (fill in the stack's real format/lint/type/test/fitness commands; enable CodeQL + Dependabot) **incl. deploy to a dev environment with a smoke test + automated rollback**; (b) **spec/doc governance** (framework-provided, ready-to-run) — `lint_spec.py` + `guard_derived.py` on PRs, the docs-site deploy, branch protection, MR template
- **Acceptance gate at finalization** — each slice independently **valuable / demoable** with a recorded user-visible outcome; a slice that isn't demoable on its own is a horizontal cut to re-slice, not a task
- **Each task is a complete reference manifest** — every applicable dimension is a spec-ID ref, `N/A — why`, or `GAP — UNRESOLVED`; **implementation-final = no UNRESOLVED gap remains**
- **`afk:` marker** — `eligible` (an agent implements *and merges* this solo) when there's no UNRESOLVED gap and no HITL trigger; else `blocked — <trigger>`. **HITL triggers (closed list):** a visual/UX decision · a product/strategy call · a legal/compliance sign-off · an external credential/access · an irreducible preference fork. **Prefer AFK** — a trigger outside this list is really an unresolved gap to resolve now
- **Coverage** — every in-scope use-case covered by ≥1 task; the walking-skeleton task exists and is first; build-order acyclic and MVP-first
- **module internals are JIT, not up front** — the architecture fixed the seams; a slice flags `design: design-first` only when genuinely complex (hard algorithm · real concurrency · cross-context saga), then its modules are designed & reviewed before coding; a simple/CRUD slice designs-as-it-TDDs

## Output
**Stable IDs** (bare type prefix): `T-` task / vertical slice (`T-001` = the walking skeleton, always first); one file `T-NNN.md` per task.
Written under `delivery/tasks/`:

| File | Captures | Format |
|---|---|---|
| `build-order.md` | dependency order of the slices, MVP-first | ordered list or Mermaid DAG |
| `T-001.md` | the walking-skeleton task (architecture end-to-end + repo scaffold + dev-deploy w/ smoke test + automated rollback) | prose |
| `T-002.md` | one task = one vertical slice; every dimension an ID ref, N/A, or resolved gap; a user-visible-outcome line | prose |
| `T-NNN.md` | …one file per slice (slice-specific UX inlined here; the `ux` dimension points at the slice's prototype screen) | typed dimension fields: behavior/domain/data/api/ux/a11y/security/nfr/integration/placement/design/tests/deps/DoD, each an ID ref or N/A · a user-visible-outcome: line · a phase: line MVP/near/deferred |

ADRs → `adr/ADR-TASK-NNN.md`
*(DERIVED & regenerate-only)*
Consumes: the use-cases / acceptance criteria, domain model, architecture (incl. the module map & seam contracts), conventions, product phasing, and the UX requirements (incl. the information architecture). The per-slice clickable prototype screen is generated **at execution time**, not up front — the task's `ux` dimension references it then.

## Excludes
writing the code (execution) · release dates/sprints (the product *phasing* MVP/near/deferred orders the work, not calendar dates) · the global UX (only slice-specific UX is produced here)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
