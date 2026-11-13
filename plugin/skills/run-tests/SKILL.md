---
name: run-tests
description: >-
  Run a task's tests and the project's gate and report whether the slice is proven — every acceptance criterion exercised at the right level, bars met. Use when a task's code is written, or for the system suite before a release. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: a task's tests to run and gate
---

# run-tests

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill runs the tests and judges what the run proves. It does not write tests or fix code: a missing test, a test at the wrong level, or a red suite goes back to implementation with a precise description, so the step that verifies is not also the step that adjusts what is verified.

It runs at two scopes: one slice's tests while a task is being built, and the system suite (the Tier-B suites of the test strategy) after work has landed or before a release.

## Slice scope
1. Run the project's gate command, as its conventions name it, plus any tier the gate leaves out that the slice touches (the integration tier, on many projects).
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/tools/check_task.py spec --task T-NNN`. It reads the brief and the test tree and fails when an acceptance criterion has no `@covers` test, a named UI state has no `@state:` test, a gap is unresolved, or a dependency is not done.
3. Judge what those two commands cannot see.

**The right level.** A fully mocked test does not prove a criterion that needs a real path.

| A criterion that is | Needs |
|---|---|
| user-observable | an e2e or system test through the real interface |
| cross-component, persistence or messaging | an integration test against real dependencies (containers, a real database or broker) |
| a pure domain rule | a unit test |

**What the tests assert.**
- Outcomes: resulting state, output and emitted events, rather than which calls were made. Each test can fail, and the edge, error and negative paths are covered as well as the happy one.
- Asynchronous behaviour on the real path: the job is enqueued, a real worker consumes it, and the observable effect is asserted by polling with a timeout under a controlled clock. Retry, idempotent re-delivery, ordering and the dead-letter path are exercised. A test that only asserts "enqueued" has not tested the job.
- A synchronous seam's degradation: the timeout, circuit-break or fallback its integration requirement names is triggered by a test.
- The changed domain logic is pinned: the mutation bar the gate enforces is met. A surviving mutant in changed logic means a boundary or a rejection reason is not asserted.

**A whole suite.** Nothing is skipped; a run that prints `N skipped` is not a clean run.

For a UI slice, three more checks belong to the slice and gate with it, because the system-level accessibility run comes too late to catch a screen the day it lands:

| Check | Pass |
|---|---|
| state coverage | every interaction state the brief's `ux` row names is exercised by a test tagged `@state:<name>` (`check_task.py` reconciles the tags) |
| accessibility | an automated scan (axe or equivalent) over every touched screen with no critical or serious finding, and the keyboard and focus path from the `a11y` row asserted in e2e |
| breakpoints | each touched screen rendered at every design-system breakpoint with no overflow and no hidden primary action |

## System scope
Run the journey and acceptance suite, the architecture fitness functions, the contract suite and the NFR-evidence tests (load, soak, chaos, security scans, accessibility), each where the tier contract says it runs.

A green run is the start, not the answer. Compare each measured result with its target — from `09-solution/test/nfr-evidence.md` where the project has it, otherwise from the requirement itself: whether p95 met the `ASR-`, whether the soak showed a leak, whether recovery stayed inside the RTO, whether load held at the stated concurrency. An accessibility run names its conformance target (the current WCAG level the project committed to) and fails on critical findings. A test that does not measure the requirement is not evidence for it.

Report one row per requirement: id · measured · bar · met. When the run is the evidence for a production promotion, hand those rows to the release step, which records them in its readiness record.

## Result
This skill writes no file and changes no code or spec. Its result is a report, written as the engine's Reporting section says, that opens with one line an orchestrator can key on:

- `VERDICT: PASS` — the gate is green, `check_task.py` is green, and every judgment above holds.
- `VERDICT: FAIL — <what>` — naming the red tests, the uncovered criterion, the wrong-level test, or the bar that was missed.

Then say which suites ran and where, and which did not. A tier that needs a deployed environment and was not run is reported as not run, never folded into a pass.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
