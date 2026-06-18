---
name: implement-task
description: >-
  Implement one prepared task as a minimal, tested vertical slice — tests first, within architecture boundaries, code in the source tree (not the spec). Use when you have a prepared task to build. Loads the shared exec core.
disable-model-invocation: true
argument-hint: a prepared task (T-NNN) to implement
---

# implement-task

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **implement one prepared task as a minimal, tested vertical slice** — tests first, inside the boundaries, code in the source tree.

## Process
1. **Branch.** Off main (`task/T-NNN-…`); never commit to main.
2. **Tests first, layered.** From the acceptance criteria, write the failing tests across every layer the slice touches — unit (domain/logic), integration (adapters/persistence), contract (`API-`/`EVT-` schemas), e2e (the user-observable path). One behavior at a time, asserted through the public interface.
3. **Implement the minimal slice.** End-to-end (entrypoint → application → domain → persistence) to green. For an empirical unknown about the slice's shape, spike a throwaway prototype first.
4. **Handle edges just-in-time.** A behavior no task anticipated → stop, don't guess; record a `GAP` and resolve it (complete / `N/A` / accept a default as an ADR) before continuing.
5. **Run enforcers and ship.** Pre-commit runs the checks → conventional commit → open one MR/PR → CI → merge. On a re-run, re-touch only the impacted code.

## Rules
- A **test-authoring task is a different shape** — its deliverable *is* the test (a system/journey acceptance test, an architecture fitness function, or an NFR-evidence test). Author it from its source spec, make it executable and **able to fail**, leave it guarding continuously; never fold it into a feature slice.
- **Author tests that pin behavior, not just cover lines** — for changed **domain logic**, assert observable outcomes strongly enough to **kill mutants** (the mutation-score gate the test run enforces on changed logic); high coverage with weak assertions fails that gate. The test strategy sets the threshold — meet it **here**, don't bounce off the gate.
- **Contracts both directions** — for each `API-`/`EVT-` the slice **consumes**, author the consumer-side contract (the consumer-driven expectation); for each it **exposes**, verify the provider against the published schema. Neither side ships unverified.
- **Spike code is deleted before the green slice** — a throwaway prototype proves shape only; delete it, then re-drive the behavior with tests (it never becomes the implementation).
- Code lives in the source tree, never in `spec/`.
- **Done:** the layered suite green locally + hooks pass → hand off for the test run, then the conformance review; MR green → merge. Report status; never mark done on red.

## Output
Written under the project source tree:

| File / target | Captures | Format |
|---|---|---|
| `src/` | the slice's implementation (entrypoint → application → domain → persistence) | — |
| `tests/unit/` | domain / logic | — |
| `tests/integration/` | adapters / persistence | — |
| `tests/contract/` | API- / EVT- schemas | — |
| `tests/e2e/` | the user-observable path | — |

(+ ADRs → `adr/ADR-BUILD-NNN.md` — a default accepted mid-implementation)
(walking-skeleton task only: `10-operate/bootstrap.md` — the human-prerequisites checklist)
*(writes CODE in the source tree — never `spec/`)*
Consumes: a single `T-NNN` + the exact spec IDs it references + the conventions + the code it touches — load only these (tight context).

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
