---
name: run-tests
description: >-
  Run a task's suite and gate on it — suite green, every acceptance criterion exercised at the right level, coverage met. Use when a task's code is written and you need to verify it. Loads the shared exec core.
disable-model-invocation: true
argument-hint: a task's tests to run and gate
---

# run-tests

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **run a task's tests and gate on them** (running them IS the verification).

## Process
1. **Prove each `AC-` at the RIGHT level.** A **user-observable** AC → an **e2e/system test through the real interface**; a **cross-component / persistence / messaging** AC → an **integration test against real dependencies** (testcontainers / real DB / real broker, not mocks); a **pure domain rule** → unit. A fully-mocked test does **not** satisfy an AC that needs a real path. **Assert observable behaviour** (resulting state / output / emitted events), **not interactions**; every AC test must be **able to fail**; cover each AC's edge / error / negative paths, not just the happy path. Then check coverage vs the task plan + the test-strategy levels.
2. **Async / job / scheduled / eventual-consistency — verify the REAL path.** Enqueue → a **real worker** consumes it → the **observable side effect** occurs; assert the eventual outcome with **poll-with-timeout (never sleep)** and a **controlled clock**; explicitly test **retry, idempotency (re-delivery is safe), ordering, and the failure / dead-letter path**. Asserting a job was enqueued is **not** verification of job processing.
3. **System / Tier-B runs (the post-merge pipeline, not one slice).** For the whole system — the **journey/acceptance suite**, **architecture fitness functions**, the **contract suite**, the **NFR-evidence tests** (load/soak/chaos/pen/SAST/DAST/a11y) — green is not enough: **interpret the evidence against its target** (did p95 meet the `ASR-`? did the soak reveal a leak? did chaos recover within RTO? did load hold at stated concurrency? did the **a11y** run meet its named **current WCAG** conformance level with zero criticals?) and record the **release-readiness verdict**. An assertion that doesn't measure the NFR is not evidence.

## Rules
- **Runs + gates + interprets evidence; never authors** — the tests are written by the implementation step (per-slice, **tests-first/TDD**) and as **Tier-B test-authoring tasks**; the test *strategy* decides which must exist. This skill *runs* a suite, checks each `AC-` is present **at the right level**, gates (coverage · mutation · NFR evidence), and emits the verdict. A missing or wrong-level test is a **FAIL back to implementation** (which authors it) — never written here. Runs at **two scopes**: a **slice's suite** inside the build loop, and the **full Tier-B/system suite** post-merge / for release-readiness.
- **Never pass on:** red tests · an `AC-` with no test **or tested at the wrong level** (mock-only where a real e2e/integration path is required) · **interaction-only assertions** with no observable-outcome check · an **async/job behaviour not exercised end-to-end** (incl. retry/idempotency/failure) · a test that **cannot fail** · coverage below target. On fail → back to implementation.
- **Mutation-score gate on changed domain logic** — the real adequacy check behind coverage %: surviving mutants in the changed domain logic mean the tests don't pin behavior; below the mutation target fails the same as a coverage gap.
- **A11y evidence names its target** — like every NFR evidence, an a11y run states its conformance target (the **current WCAG** level) and **fails on criticals**; an a11y check with no stated level/threshold is not evidence.
- **Verdict** (the autonomous loop keys on this): emit one line — `VERDICT: PASS` when the suite is green AND every `AC-` is exercised AND coverage meets target; else `VERDICT: FAIL — <red tests / untested AC- / coverage gap>`. Never report PASS by skipping or weakening a test.
- Code lives in the source tree, never in `spec/`.

## Output
Primary output: a tight pass/fail result + the VERDICT line — no files (standalone: at the working root).

| File / target | Captures | Format |
|---|---|---|
| `08-delivery/verification/test-run.md` | OPTIONAL, only if persisted: suite · level · pass/fail · coverage vs target · the release-readiness verdict (for a Tier-B/system run) | — |

(no spec or code changes)
Consumes: the `T-NNN` package + its acceptance criteria (`AC-…`) + the produced tests/code.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
