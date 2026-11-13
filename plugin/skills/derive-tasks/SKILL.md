---
name: derive-tasks
description: >-
  Break a spec into small, vertically sliced task briefs a coding agent can build from — each self-contained, risk-tiered, phase-tagged and dependency-ordered, walking skeleton first. Use when the spec needs turning into build-ready work.
disable-model-invocation: true
argument-hint: a spec, design docs, or a feature to break into tasks
---

# derive-tasks

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **task breakdown** — turning a recorded spec into the smallest set of vertical slices that builds it.

## What a good brief is
A brief is what an agent reads instead of the spec. It should be buildable from the brief and the code alone: the acceptance criteria carry their text, the rules that bind the slice are stated in a line each, and what the slice deliberately leaves out is named. IDs stay on every item so tools and later changes can find it, but nobody should need to follow one to understand the task. A brief that sends its reader to twenty other files has moved the work, not done it.

Briefs exist for work that adds behaviour. A bug fix, a copy change, a refactor or a dependency bump is `routine` and needs no brief (the exec engine says what it owes).

## Method
1. **Walking skeleton first.** The first task wires the architecture end to end with one trivial path, scaffolds the repo, sets up the gate and the hooks the conventions define, and really deploys to the first environment of the promotion path with a smoke check and a rollback. It is `critical`. Its environments and pipeline come from the infra decisions and the delivery mode, not from here.
2. **Slice vertically.** Cut each use-case into the narrowest complete path through every layer it needs (schema → domain → api → ui → tests) that someone could demo. Size a slice to one agent session. A slice of one layer is not a task.
3. **Write the brief** (the table below). Quote each acceptance criterion's text; state each binding rule as `ID — what it requires`; list what the slice touches; name the non-goals.
4. **Set the tier** from what the slice touches, not from its size: `critical` for a new aggregate or context, a schema or data migration, authentication, authorization, erasure, billing or another money or legal path, a model seam, or any one-way door; otherwise `feature`. Give the reason in a few words.
5. **Resolve gaps.** An undecided point is `GAP <what is missing> — <owning area> — UNRESOLVED` and forces one choice: complete it in the owning area, mark it `N/A — why`, or accept a default as an ADR. For a visual or product decision, propose a concrete default for the user to ratify.
6. **Order.** Tag each task's phase (MVP · near · deferred) and dependencies; the build order is the topological sort, MVP first.

## One change to an existing product
When the product exists and a single change is being specified, write just that brief. There is no walking skeleton to add and no build order to re-derive: set the tier and what the brief depends on, quote the acceptance criteria as they now read, and add one line for it to `build-order.md`. A `routine` change gets no brief at all.

## The brief
One file per task, `T-NNN.md`, a single `field | value` table. Multi-line cells use `<br>`.

| field | value |
|---|---|
| `tier` | `feature` or `critical` — the reason in a few words |
| `phase` | `MVP` · `near` · `deferred`, then `afk: eligible` or `afk: blocked — <trigger>` |
| `status` | `todo` · `in-progress` · `done` · `blocked — <why>` |
| `outcome` | the user-visible result, one sentence |
| `behavior` | one line per `UC-`; under it one line per `AC-` with the criterion's text: `AC-014a — Given … When … Then …` |
| `touches` | the modules, seams, tables and screens the slice changes (`MOD-`, `API-`, `EVT-`, `IF-`, paths) |
| `rules` | the cross-cutting obligations that bind this slice, each `ID — one line` (`SEC-`, `ENTL-`, `NFR-`, `DATA-`, `OBL-`, `ML-`, `SLO-`, `AEV-`); `none` when there are none |
| `non-goals` | what the slice deliberately does not do |
| `tests` | the tiers this slice needs and the edges that matter |
| `depends` | the `T-` ids it waits for, or `—` |

Add only when they apply:

| field | when | value |
|---|---|---|
| `ux` · `a11y` · `prototype-review` | the slice changes a screen | `ux`: the journey and screen by id, `states: a · b · c`, and the prototype path. `a11y`: the keyboard and focus path and the success criteria that apply. `prototype-review`: `frozen — <path>` once a human has reviewed it, or `waived — <why>` |
| `human-prereq` | the slice needs a credential or external setup | the config key and where it is set, never the value |
| `design` | the slice is `critical` or genuinely complex | `design-first — <path under 10-delivery/impl-design/>` |
| `review` | the slice is `critical` | `pending`; the fresh-context reviewer sets `PASS` |

## Rules
- **One owner per acceptance criterion.** Every in-scope criterion is owned by exactly one task; a later task that builds on it depends on the owner rather than repeating the criterion. That is what makes a done-claim checkable: `check_task.py` holds the owning task to a `@covers` test for each of its criteria.
- **`afk: eligible`** means an agent can finish the task without a human: no unresolved gap and none of these triggers — a visual or UX decision, a product or strategy call, a legal sign-off, an external credential, or a merge the project's review policy reserves for a person. Otherwise `afk: blocked — <trigger>`, with the ask queued in `spec/_human-input.md`. Two cases the linter checks: a task with a `human-prereq` is eligible only when that credential is `provisioned` in `_provisioning.md`; a task that changes a screen is eligible only when its prototype is `frozen` or explicitly `waived`, because an unreviewed screen is a visual decision nobody made.
- **A screen binds accessibility.** A brief with a `ux` cell also carries `a11y`. A slice that only reuses existing design-system components on an existing screen says `ux | N/A — reuses DS-… on SCR-…` and needs no prototype.
- **The credential register.** Keep the spec-root `_provisioning.md` in step with the briefs' `human-prereq` cells: one row per credential or config key with its owner, the tasks that consume it, and its state. Preserve existing state and evidence when refreshing it.
- **Design is just in time.** The architecture fixed the seams; a `critical` slice gets a short design note before it is built (`derive-impl-design`), everything else is designed while it is test-driven.
- **Deferred work stays coarse.** Give `near` and `deferred` phases one line each in the build order until they are about to be built; briefs written far ahead go stale before anyone reads them.

## Output
**Stable IDs** (bare type prefix): `T-` task (`T-001` = the walking skeleton). Written under `delivery/tasks/`:

| File | Captures | Format |
|---|---|---|
| `build-order.md` | the slices in dependency order, MVP first, each with its one-line outcome and what it depends on; later phases as one line each | ordered table or Mermaid DAG |
| `T-NNN.md` | one brief per task about to be built | the `field \| value` table above |

Also keeps the spec-root `_provisioning.md` register in step (see Rules).
ADRs → `adr/ADR-TASK-NNN.md`
Consumes: the use-cases and acceptance criteria, the domain model, the architecture's module map and seams, the conventions, product phasing, and for UI slices the journeys and screen inventory. Detailed schema is not an input — it emerges during implementation.

## Excludes
writing the code · release dates or sprints (phasing orders the work, not the calendar) · the global UX (only slice-specific UX is settled here)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
