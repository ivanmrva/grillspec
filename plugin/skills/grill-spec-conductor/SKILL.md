---
name: grill-spec-conductor
description: >-
  START HERE to spec, design, plan, or build a project or feature end to end. The front door and orchestrator: it reads the spec, works out the current state, recommends the smallest next step, and runs the chosen area. Use it whenever work spans more than one area.
---

Each area is the skill **`grill-<id>`** or **`derive-<id>`**. The shared engines are under `${CLAUDE_PLUGIN_ROOT}/grill-shared/`: `grill-engine.md`, `derive-engine.md`, `exec-engine.md`; the decide-vs-ask test is `decision-classes.md`; the rules every artifact follows are `house-rules.md`; the output tree, profiles and spec-root files are `repo-layout.md`. You orchestrate; the area skills and engines do the interviewing, deriving and building. Everything writes into one `spec/` tree.

For situational modes, read `${CLAUDE_PLUGIN_ROOT}/grill-shared/conductor-playbook.md` when one applies: starting from an existing document, migrating a body of docs, brownfield import, changing already-built work, revising a prototype or design note, and the operations lifecycle.

## Lean by default
The aim is the smallest spec that lets the build proceed without guessing. An area, a file, a rule or a gate earns its place by having a reader — a later step, a tool, or a person who will act on it. Recommend the smallest profile that fits, offer the next area only when something downstream needs it, and treat spec that restates code or another area as a defect to remove, the same as a gap. Growing the spec when a real need appears is cheap; keeping unread spec consistent is not.

## Building from scratch, or changing something that exists
Work out which of the two you are in first; they use very different amounts of this system.

**From scratch** — there is no product yet, or a whole new product area is being designed. Walk the in-profile areas in dependency order, as Session start below describes.

**Ongoing work** — the product exists and the user brings a change: a bug, a tweak, a feature. Once the walking skeleton is built this is the normal case, and it needs no scan, no menu and no dashboards. Size the change with the exec engine's risk tiers and do what that tier owes:

| The change | What happens |
|---|---|
| `routine` — a bug fix, a copy or visual tweak, a refactor, a dependency bump | straight to `implement-task`: a failing test, the fix, the gate. The spec is touched only where a statement in it is now false. |
| `feature` — new behaviour in an existing part of the product | amend what the change alters and nothing else: the acceptance criteria, plus any rule it changes in the area that owns that rule, asking the user only what the spec and the code cannot answer. Then one brief (`derive-tasks`, for this slice only) and `implement-task`. |
| `critical` — a new aggregate or context, a migration, authentication, authorization, erasure, billing, a model seam, a one-way door | as `feature`, plus an ADR where the change embodies a decision, a design note before coding (`derive-impl-design`), and a fresh-context `conformance-review` after. |

Find what a change touches by reading the area that owns the behaviour, or with `impact.py <IDs>`; leave the rest of the spec unread and unchanged. Run `lint_spec.py` after a spec edit and fix what the edit caused. Findings that were already there are not this change's job: mention their count once, and offer `audit-spec` as separate work. Several small related changes can share one brief and one push.

In ongoing work most skills stay unused, and that is the intended state: an interview or derivation skill runs only when a change reaches its area, and then only to amend it.

A project that already has code or documents but has not used this system, or was built with an earlier major version of it, is adopted once before ongoing work starts (playbook: Adopting an existing project).

## First session — settle the two project settings
When `.grillspec/project.json` is absent (`python3 ${CLAUDE_PLUGIN_ROOT}/tools/project_config.py` says so), ask the two questions it holds before anything else. Both are facts only the user has; lead each with your recommendation and its reason, then write the answer with `project_config.py --set profile=<p> --set delivery=<d>`.

| Setting | Recommend | When |
|---|---|---|
| `profile` | `lite` | a solo or pre-launch product: vision, constraints, domain, acceptance criteria, a few quality targets, a thin architecture |
| | `standard` | the product handles personal data, money or paid tiers, or has a model capability whose quality must be gated |
| | `regulated` | the documents themselves are a deliverable — an auditor, a regulator or another team reads them |
| `delivery` | `trunk` | one person, no production users yet: work lands on the default branch, verification is local, CI only deploys |
| | `pr` | production users or more than one contributor: a branch and pull request per task, the full CI gate before merge |

Either setting can be raised later; say so. For a project that already has a spec, read the tree and propose the profile it actually needs rather than the one its size implies.

## Session start — from scratch, or when the user asks where things stand
1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/tools/lint_spec.py`. Its ERRORs are the structural truth (paths, headers, references, the profile, the timeless rule, unratified values once tasks exist); fix or surface them before anything else. Then scan the area outputs and rebuild the state (below).
2. Offer a short menu grounded in what the scan found, with one recommended default: the next area the profile calls for; resume an area in progress; fix a cross-area inconsistency; test the riskiest untested bet; an area the user names; migrate existing docs; audit the spec (`audit-spec`); once the solution is ready, prepare delivery (`derive-conventions` → `derive-tasks`); once tasks exist, work the next task, or every ready task unattended. Show what is blocked and what unblocks it. Optional areas (market, customer discovery, monetization, go-to-market, growth) appear only when the user asks for them.
3. Run the chosen area yourself. The decision-mode solution areas are small and read the same inputs, so after the architecture write them together in one session rather than one session each.

   The area skills are reference documents (`disable-model-invocation: true`), not agents: load the skill's `SKILL.md` and its engine and carry out the interview or derivation in line, or in a subagent you brief with that text. One focus per session; finish or park it, then start again. Start only what the user chose.

When several sessions run at once, keep one area per session. Each area owns its own folder, so parallel areas do not contend; after a merge, rebuild the cross-area state from the tree.

## What you give each skill, and what you take back
The area skills know nothing about this system — no gates, no tree, no awareness of each other. That keeps them usable standalone, and makes the orchestration yours:
- **Input.** Look the area up in `${CLAUDE_PLUGIN_ROOT}/grill-shared/dependencies.json` (`consumes` = where to start, not a boundary; `profile` = the smallest profile it belongs to; rendered at `${CLAUDE_PLUGIN_ROOT}/docs/DEPENDENCY-GRAPH.md`). An interview or derivation integrates many concerns, so hand it every upstream area that exists, with the `consumes` set marked as the starting point. A build task is the opposite: `implement-task` gets its brief and the code, because a brief is written to stand alone.
- **Target.** The working root (`spec/`) and the exact folder for its artifact, from `repo-layout.md`.
- **Depth.** The project profile, so the skill captures the core for that profile and leaves the rest absent.
- **Harvest.** Read what it wrote for terms, actors, bets and decisions. Then reconcile the system-wide glossary and actor views, run `lint_spec.py`, check cross-area consistency, and propagate (below).

## The state you rebuild each run
Three views, reported separately because they answer different questions:
- **Spec health** — per in-profile area, a maturity level on a closed scale so two sessions rate alike: `L0` no content · `L1` framed (scope and first content, open points remain) · `L2` consistent (invariants pass; every point Resolved, Deferred or N/A) · `L3` validated (its load-bearing bets Validated or Accepted-risk).
- **Bet health** — of the critical bets recorded across areas, how many are Validated / Testing / Accepted-risk / Untested / Invalidated, plus kill-criteria status. A consistent spec beside an untested bet is the point of keeping these apart.
- **Delivery health** — once tasks exist: `python3 ${CLAUDE_PLUGIN_ROOT}/tools/check_task.py spec` prints every task's tier, status, criteria covered and open items, computed from the tree.

The stage chain, the per-area folders and the gates are in `repo-layout.md`; consult it rather than restating it. What the tree cannot show: discovery runs first and never closes; `derive-impl-design` is written just in time for a `critical` slice; the per-task loop is `implement-task`, followed for a `critical` task by `conformance-review`, with any failure routing back; the exec engine's queue rules extend that loop across the build order when the user asks for an unattended run; `prototype` answers one empirical question at any stage; the `generate-*` skills publish from the spec on demand.

## Readiness — offer what is answerable
Offer a topic when its prerequisites have content, not when its area is merely started: nobody can answer a subscription question before a product function exists. A topic whose prerequisite is empty is recorded as `Deferred` with the trigger that reopens it, and promoted when the trigger is met. At the foundation, accept coarse answers ("roughly these areas") and let them sharpen later.

**Gates**, each counting only in-profile areas:
1. **Desirability** (soft, early) — the riskiest desirability bets are named with a test plan before deep speccing.
2. **Architecture-readiness** — the in-profile foundation and requirement areas (design system and ux for a UI product) are consistent, and every critical bet is Validated or explicitly Accepted-risk. Proceeding on accepted risk is fine; scope the first build to test it cheaply.
3. **Implementation-readiness** — the solution areas the profile includes are consistent, including the module map and seam contracts.
4. **Delivery-readiness** — conventions exist; a walking-skeleton task is first; every in-scope use-case is covered by a task and every acceptance criterion owned by exactly one; the build order is acyclic. A cross-cutting rule reaches the build only through a task brief's `rules` cell, so confirm the ones in scope appear there.
5. **Per-task done** — as the exec engine defines it.

Gates are readiness signals, not locks: a skill can always be invoked directly.

## Next task
The build order is a hard constraint (a task waits for the tasks it depends on; the walking skeleton is first); product phasing (MVP → near → deferred) is the priority within what dependencies allow. The next task is the earliest-phase task whose dependencies are done. A brief is ready to build when it has no `UNRESOLVED` gap; a gap is surfaced at that task, the last responsible moment, and resolved by completing it, marking it N/A, or accepting a default as an ADR.

Each brief carries a risk tier (`routine` · `feature` · `critical`) that decides how much process it owes; raise a tier when the work turns out riskier, and say so. For a UI slice whose screen is new, generate and review the prototype when the brief is finalized (`generate-ui-prototype`) so an unattended run builds against an approved screen; a slice the design system and screen inventory already determine needs none.

## Consistency across areas
Per-area open lists are caches; the truth is recomputed over the whole tree, because a correct new fact can break another area: a renamed term invalidates security or ux, a plan with no entitlement rule is a gap, a requirement cites a removed flow. Route each break to the owning area as an open point. An `Invalidated` critical bet is the same kind of event coming from the market: it can reopen scope, vision, even the domain.

## Change propagation
A change touches the areas it actually changes, and nothing else — there is no layer-by-layer walk.
1. Identify what changed: the IDs you just touched, or `python3 ${CLAUDE_PLUGIN_ROOT}/tools/impact.py --since <ref>`.
2. Compute the impact set: `impact.py <IDs…>` lists the downstream spec files, tasks and the tests that claim those IDs, upstream first.
3. Re-work that set and only that set: the owning skill updates each affected artifact in place (smallest change in meaning, re-authored so it reads as one document); affected briefs are re-finalized; the listed tests are re-run and the code under them changed.
4. Re-verify with `lint_spec.py` and the project's gate.

Worker skills stay unaware of the rest of the system; they name the IDs they changed in their hand-off, and propagation is yours whenever you are driving.

## Skill kinds
- **Interview (`grill-*`)** — elicits what only the human or the market holds: vision, domain, the values behind requirements. May ask.
- **Derivation (`derive-*`)** — writes from the recorded spec; decides engineering trade-offs, surfaces user-owned values for ratification, and raises a gap to the owning interview skill rather than asking. Confirm its inputs exist before running it.
- **Execution** (`implement-task` · `conformance-review` and the operate skills) — acts on the code; governed by `exec-engine.md`.

## What you write
You own no area artifact and write no ADRs. At the spec root you keep three reconciled views, each a table:

| File | Holds |
|---|---|
| `glossary.md` | the system-wide vocabulary reconciled from the areas — `term · definition · context`, one term one meaning |
| `actors.md` | one actor roster — personas, domain roles and boundary actors merged: `actor · type · owning area · description` |
| `_readiness.md` | per in-profile area: `area · status · maturity (L0–L3) · open count · gate state` |

The ADR index, the bet register and the risk register are read from the areas on demand, not stored. A file at a path `repo-layout.md` does not list is relocated or merged on scan.

## Release readiness
The system has no concept of a release; promoting to production is the user's action (`deploy-release` runs it). When they decide to ship, the things worth checking are: every MVP task done; `check_task.py` clean; quality targets backed by measured evidence; the objectives and their alerts in place where the profile includes them; required data migrations done; the critical obligations and security rules verified; sign-off from the named owners. In `trunk` delivery this is also the moment to run the CI jobs that are otherwise dispatch-only (security scan, accessibility, visual baseline, mutation), and `audit-build` gathers the evidence. This is a checklist to consult, not a lock.

Friction that is a defect in this system itself follows the house rules' plugin-feedback route; mention the count of entries in `GRILLSPEC-FEEDBACK.md` in your end-of-run report.
