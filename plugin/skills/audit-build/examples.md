# audit-build — worked example

Illustrative: it shows the shape of a pass and of a finding, not required content.

A task-management product at the `standard` profile with `trunk` delivery, 34 tasks done, preparing its first production release. The user runs `audit-build` with the defaults (`--depth attest --scope release`). `lint_spec.py` reports no ERROR, so the spec is fit to audit against.

## Phase 0 — mechanical baseline
```
check_task.py spec           → 34 task(s): done 34 · ERROR T-021 claims done but: no `@covers` test for AC-140c
check_no_fakes.py --strict   → clean
check_no_skips.py --strict   → clean
check_orphan_tests.py        → clean
check_config_drift.py        → ERROR: code reads MAIL_FROM, not declared in environments.md
check_mock_budget.py         → ERROR: tests/integration/billing.int.test.ts mocks the database
check_test_tiers.py --require --require-all-tiers → clean · unit=212 integration=41 contract=9 e2e=6
project gate (pnpm verify)   → green
```
Three errors, decided by the tools: all `blocking`. The rest of the audit is the reading the tools cannot do.

## Dispatched jobs (`trunk` delivery)
```
integration suite   → green
security scan       → green
accessibility       → 1 serious finding on the task-detail screen
visual baseline     → not run — needs the operator: gh workflow run visual-baseline.yml
mutation            → 61% on changed domain logic (bar 70%)
```

## Phase 1 — a done-claim the tag does not prove
Sample: the 3 `critical` tasks, plus `T-019`, whose tests are the thinnest. The trace lists `tests/unit/reschedule.test.ts` for `AC-118` ("an overdue task is moved to the next working day"). The test calls the scheduler and asserts only that `save` was called.

→ `blocking · T-019 · AC-118 · tests/unit/reschedule.test.ts:14 · the test does not assert the new due date, so the criterion is unproven · owner: the task (status back to in-progress).`

`T-027` added a `tenant_id` column and a backfill migration, and its brief says `tier | feature`.

→ `important · T-027 · a data migration built as a feature: no design note, no independent review · owner: raise the tier to critical and run the review.`

## Phase 2 — what only the whole tree shows
`vitest.config.ts` excludes `src/billing/**`. Four test files there carry `@covers` tags for `AC-203a`–`AC-203d`; none of them runs.

→ `blocking · AC-203a–d · vitest.config.ts:22 · tagged tests are excluded from the run, so four criteria count as covered and are not tested · owner: remove the exclusion, then fix what fails.`

`.grillspec/no-fakes-allow.txt` has one entry, `src/dev/seed.ts — local seed data`, and the file is not reachable from a production entrypoint. Reason still true; no finding.

## Verdict (in `build-audit-report.md` at the project root)
```
BUILD ATTESTATION: NOT-ATTESTED  (5 blocking, 3 important)
scope: release 1 (34 tasks) · profile: standard · delivery: trunk
depth: attest (read 4 of 34 tasks) · commit: 9f3c1a2 · spec: lint clean
Top fixes:
  1. AC-140c has no test (T-021) · AC-118 test asserts nothing (T-019)      → the tasks
  2. billing tests excluded from the run (AC-203a–d)                        → remove the exclusion
  3. MAIL_FROM undeclared · integration test mocks the database            → environments.md · the test
  4. mutation 61% < 70% · one serious accessibility finding                 → the tasks concerned
  5. T-027 under-tiered                                                     → raise the tier, run the review
Not run: visual baseline (operator dispatch).
```
After the fixes land, a new run covers the whole tree again in Phases 0 and 2 and re-reads only the changed tasks in Phase 1.
