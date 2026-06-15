# implement-task — worked example

Building **T-014 — Reschedule a booked job** as one minimal, tested vertical slice. Tests first, inside the Scheduling boundary, code in the source tree (never `spec/`).

Branch `task/T-014-reschedule-job` off main. From the acceptance criteria, the failing tests go in first, layered across every layer the slice touches:

```
tests/unit/job.reschedule.spec.ts          AC-014c lead-time, AC-014b owning-branch (domain rule)
tests/integration/job-repo.slot.spec.ts    AC-014d slot-taken — real Postgres (testcontainer)
tests/contract/job-rescheduled.evt.spec.ts  EVT-JobRescheduled — provider vs published schema
tests/contract/notify-consumer.spec.ts      consumer-side expectation on the field-notify API we CONSUME
tests/e2e/reschedule.e2e.spec.ts            AC-014a happy path — POST /jobs/{id}/slot through the real interface
```

Then the minimal slice, entrypoint → application → domain → persistence, to green. The slot-overlap query had an unknown shape → spiked a throwaway prototype, confirmed the index, **deleted the spike**, re-drove it with the integration test.

One edge surfaced that no task anticipated — a customer already SMS-confirmed when the slot moves. Didn't guess: recorded a `GAP`, resolved it as `N/A` for this slice (notification is a downstream task), noted in the task record before continuing.

## Done-gate (the bar before hand-off)

```
T-014 done-gate
  [x] layered suite green locally   unit · integration(real PG) · contract · e2e   (12 passed, 0 skipped)
  [x] domain tests pin behavior     lead-time boundary asserted exactly (2h ok · 1h59 reject) — strong enough for the run's mutation gate, not just coverage
  [x] consumer contract authored    field-notify API we consume — expectation pinned & verifiable
  [x] provider contract verified     EVT-JobRescheduled matches published schema
  [x] pre-commit hooks pass          format · lint · type · SAST · audit · fast unit · boundary fitness
  [x] conventional commit + one PR opened
  [ ] CI green → merge               (awaiting pipeline)
→ hand off for the test run, then the conformance review. NOT marked done on red.
```
