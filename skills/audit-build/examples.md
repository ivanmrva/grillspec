# audit-build — worked example

A task-management product with 34 merged tasks, preparing its first production release. The user runs
`audit-build` (default `--depth attest --scope release`). A clean whole-spec audit is the precondition — it
passed, so the build is attestable.

## The ground truth it reads — the tier contract in `test/levels.md`
The strategy's machine-readable tier contract is what the mechanical gates check against. This is the exact
shape `derive-test-strategy` emits and the verifiers parse (header must carry `tier` + `mock-ceiling`):

```
## Tier contract
| tier        | real-deps          | may-mock              | mock-ceiling  | target-env | coverage-bar | mutation-bar |
|-------------|--------------------|-----------------------|---------------|------------|--------------|--------------|
| unit        | none               | —                     | none          | local      | 80%          | 70%          |
| integration | db, broker         | third-party-network   | boundary-only | local      | 70%          | —            |
| contract    | provider, consumer | —                     | none          | local      | —            | —            |
| e2e         | all                | —                     | none          | preview    | —            | —            |
```

## Phase 0 — mechanical aggregate baseline (across all 34 tasks)
```
check_task_record  → 33/34 green · T-021 record cites a VERDICT file that isn't on disk
check_test_tiers --require → ERROR: no `unit` suite exists though the contract declares it
check_mock_budget  → ERROR: tests/integration/billing.int.test.ts mocks the db (boundary-only tier)
check_e2e_target   → clean
check_operate_records → ERROR: deploy-prod-1.0.0.md references T-402 (resolves nowhere)
```
The mechanical layer already decided these — they become `blocking`. The audit now spends its effort on
what the tools can't see: whether the *set* of green verdicts actually holds.

## Phase 1 — ledger integrity (a rubber-stamp the per-task review couldn't catch about itself)
`T-021`'s record reads `conformance | review | verdict | review-report.md | PASS`, but no independent
`VERDICT: PASS` for `T-021` exists under `spec/10-delivery/verification/`. The per-task review *produced*
that row, so it can't audit it.

→ `blocking · ledger · T-021 · conformance row claims PASS but no independent verdict is on disk — a
rubber-stamped done-claim · route: re-run the conformance review for T-021 in a fresh context.`

## Phase 2 — cross-task emergent (a defect that lives BETWEEN tasks)
`AC-118` was recorded covered-and-passing by `T-019`. `T-030`, merged nine days later, refactored the
scheduler and left `it.skip('reschedules overdue', …)`. Every per-task gate was green at its own merge; only
the aggregate re-run sees the coverage *died*.

→ `blocking · emergent · AC-118 · covering test skipped by a later task (T-030) — coverage recorded at
T-019 no longer holds · route: a focused-change T- to restore the test.`

Suite-shape check: the contract declares a `pyramid`, but the actual tree is unit=0 · integration=41 ·
e2e=52 — top-heavy and unit-less.

→ `blocking · emergent · the suite contradicts the declared pyramid (unit=0, e2e=52) — the distribution the
strategy ratified was never built.`

## Phase 4 — operate reconciliation
`deploy-prod-1.0.0.md` names `T-402`, which exists in no task file, and an env `prod` that *is* on the
promotion path (ok). The dangling `T-` is the finding.

→ `important · operate · deploy-prod-1.0.0.md references T-402 which resolves nowhere — a broken operational
trail · route: correct the record (append-only — fix forward, don't rewrite history).`

## Verdict (written to `build-audit-report.md` at project root)
```
BUILD ATTESTATION: NOT-ATTESTED  (4 blocking, 1 important)  ·  scope: release r1 (34 tasks)  ·  depth: attest (sampled 6 of 34)  ·  commit: 9f3c1a2
Ledger:    T-021 conformance verdict missing on disk (rubber-stamp)
Emergent:  AC-118 coverage skipped by T-030 · suite contradicts declared pyramid (unit=0)
Operate:   deploy-prod-1.0.0.md → dangling T-402
Top fixes: 1. re-run conformance review for T-021   2. restore AC-118 test (new T-)
           3. build the unit tier / rebalance to the pyramid   4. fix the deploy record
```
The opt-in release gate `check_release_attestation.py` reads this verdict — with `NOT-ATTESTED` it exits
non-zero, so a team that wired it as a required check cannot ship r1 until the four blockers clear. A clean
run would instead write `BUILD ATTESTATION: ATTESTED` and the gate would pass. `--depth deep` would replace
the sampled Phase 3 with an independent code-vs-spec re-judgment of all 34 tasks.
