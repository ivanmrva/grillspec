---
name: conformance-review
description: >-
  Independent, fresh-context review of a task's code against the spec: boundaries, contracts, data, security, quality bars, rendered UI (blocking) and design health (advisory). Use when a critical task is built and before it is marked done, or when asked to review built work against the spec.
argument-hint: the code and task to review against the spec
---

# conformance-review

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill is the independent review of built code against the spec. Lens A, conformance, decides the verdict. Lens B, design health, is advice.

## When it runs, and who runs it
| Trigger | Scope |
|---|---|
| a `critical` task, before it can be done (the engine's risk-tier table) | `changed` — the task's diff and its blast radius: callers, callees, the seams it touches |
| any task, when the user or orchestrator asks | `changed` |
| a wider re-check on request | `full` — the same checks over the whole codebase |

The review is worth something only because it is independent, so it runs in a fresh context — a subagent or a separate session that did not write the code. Start from the brief, the design note it names, the diff and the code around it, not from the implementer's account of what was done.

It complements the host's own code review. That one looks for general correctness and regressions; this one looks for divergence from the spec and for architectural erosion. Use the same discipline: check each finding against the actual code before reporting it, and tag it `blocking`, `important`, `nit` or `suggestion`.

Review against the spec the project has. Its profile decides which areas exist; an area the profile leaves out is not a finding.

## Lens A — conformance (blocking)
Throughout, "evidenced" means a test exercises the behaviour. Code that looks right is not evidence.

**Architecture.** Check it first and on every round. A re-run to green is when a shortcut across a boundary is most likely, and a passing test hides it.
- Dependencies point inward and form no cycle, and each module's real dependencies match its declared `role:`.
- One context reaches another only through a published contract or event.
- Persistence sits behind a port; no ORM or DTO type crosses a layer.
- A module exposes no public surface beyond what the architecture and the design note give it.
- A cross-module flow follows the architecture's key sequences, including the failure and compensation branches.
- Every fitness function the architecture names exists as an executable rule.
- The shipped pipeline matches the ratified promotion path, and the runtime contract holds: the `preflight` command, the health and readiness endpoints, the startup order.

**The rules the brief names**, by kind:

| Kind | Confirm |
|---|---|
| contracts (`API-`, `EVT-`) | the implementation matches the published contract, as provider and as consumer; run `check_contracts.py` when the slice touches one |
| data (`DATA-`) | the model, residency and retention of each class are honoured, and a retention, TTL or deletion trigger the slice owns is exercised |
| security and entitlements (`SEC-`, `OBL-`, `ENTL-`) | a test invokes the deny path, the over-limit path or the lapsed-billing path |
| quality (`NFR-`, `ASR-`) | measured evidence against the stated bar |
| signals (`SLO-`, `AEV-`) | the telemetry and analytics events are emitted and asserted |
| model capabilities (`ML-`) | the eval result meets its bar |

**Rendered UI.** Judge a UI slice on the running app, because a screen read only as code has not been reviewed. Open every screen the slice touches and walk the journey's `SCR-` path from `prototypes/ui/flows.md`. Compare each screen with its prototype: layout, microcopy, and every named interaction state reachable and realised. Confirm styling comes only through `DS-` tokens and components, walk the keyboard and focus path from the `a11y` row yourself, and render at the design-system breakpoints. A slice whose `ux` row says it only reuses existing components still gets this look: the reuse claim spares it the prototype review, and a composition or flow change hiding behind it is a blocking finding.

**Honest production code.** Run `check_no_fakes.py`, `check_no_skips.py`, `check_orphan_tests.py`, `check_deploy_real.py` and `check_migration_real.py`, then add the judgment a pattern scan cannot make:
- a fake the scan missed, such as a canned response behind an unconfigured-dependency branch;
- a deploy that is statically present but not behaviourally proven — the proof is a green smoke or e2e run against the real environment, and where that environment cannot run yet the task is `blocked`, not passed;
- for the slice's e2e, the list of criteria and flow branches it does not exercise, each with its reason. Coverage at a cheaper tier, as the test strategy allows, is a valid reason. Steering around a path because a dependency might not be ready is not, and blocks like a skipped test. Writing the list out is what exposes a weakened e2e;
- the waiver files (`.grillspec/no-skips-allow.txt`, `no-orphans-allow.txt` and their siblings): every entry still needs a reason that is true today.

**Traceability, both directions.** Forward: every criterion in the brief has implementing code and a passing test — `python3 ${CLAUDE_PLUGIN_ROOT}/tools/check_task.py spec --trace` prints the criterion → test matrix, and `--task T-NNN` should show the missing review as its only open item once any held-out tests are in. Backward: every behaviour in the diff is demanded by a spec ID. `check_orphan_tests.py` covers the test tree; you judge code that no test pins. Behaviour the spec does not ask for is drift even when someone asked for it in chat, so it goes to the spec first and is not waved through.

**Held-out criteria.** In an orchestrated run the orchestrator may have withheld one or two criteria from the implementer. You hold the full brief: write fresh acceptance tests for the held-out criteria, tagged `@covers`, or run the system tests that already cover them. A held-out criterion that fails means the slice was fitted to the visible tests, and blocks.

## Verdict
`VERDICT: PASS` when Lens A is clean. Otherwise `VERDICT: FAIL — <the blocking findings>`, and the implementer fixes them inside the boundaries. When the spec itself is wrong, report that as a gap for the area that owns it; the code is not bent around a bad spec, and the spec is not edited to match the code.

On `PASS` for a `critical` task, set the brief's `review` row to `PASS`. That row is the one durable trace of the review and the only thing this skill writes under `spec/`; `check_task.py` reads it, which is why the reviewer sets it and the implementer does not. After a `FAIL` you look again once the fixes are in. Two rounds is the limit: a disagreement that survives them goes to the human with both positions, as the engine says.

## Lens B — design health (advisory)
After the verdict, name what would make the code easier to change. It does not affect the verdict.

- A **module** is an interface plus an implementation; the **interface** is everything a caller must know. A module is **deep** when much behaviour sits behind a small interface and **shallow** when the interface is about as complex as the implementation. Shallow modules that could be deepened are the main candidates (the deletion test: would removing the module push its complexity into callers, or just remove a hop?).
- **Information leakage** — one design decision spread across several modules — is a candidate to consolidate.
- One adapter behind a port is a hypothetical seam; two make it real. Recommend an abstraction when the second one exists.

Cheap candidates can be refactored under a green suite as part of the task; larger ones become their own task. Where a candidate is rejected for a reason that will keep holding, recommend recording it as an ADR so a later review does not raise it again.

## Output
A findings report to the implementer or orchestrator; under `pr` delivery, post it on the pull-request thread as well. Nothing is written under `spec/` except the `review` row; acceptance tests for held-out criteria go into the test tree.

| Part | Content |
|---|---|
| verdict | the `VERDICT:` line, then one or two sentences on the state of the slice |
| findings | table: severity · where (`path:line`) · what diverges · the spec ID it diverges from |
| e2e not-exercised list | each criterion or branch the e2e leaves out, with its reason |
| held-out criteria | each one and its result, when the run withheld any |
| checks | which tools and manual checks ran, and which could not |
| design candidates | Lens B, in priority order |

Reads: the built code, the brief and its design note, the spec passages and ADRs the brief points at, the conventions, the glossary.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
