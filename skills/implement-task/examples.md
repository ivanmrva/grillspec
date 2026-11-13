# implement-task — worked example

Illustrative. Building T-014, "Reschedule a booked job": a `feature` task (new behaviour inside the existing Scheduling context), so it owes its brief, test-first work and the gate. The project's `delivery` is `trunk`.

The brief's `behavior` row carries four criteria with their text, for example `AC-014c — Given a job starting in under 2 hours, When the dispatcher reschedules it, Then it is rejected as lead-time-violated`. Its `rules` row names one obligation: `SEC-031 — only a dispatcher of the owning branch may move a job`.

The tests went in one at a time, each seen failing before its code existed:

```
tests/unit/job.reschedule.spec.ts           @covers AC-014c (2h accepted, 1h59 rejected) · AC-014b owning branch
tests/integration/job-repo.slot.spec.ts     @covers AC-014d slot taken — real Postgres in a container
tests/contract/job-rescheduled.evt.spec.ts  EVT-JobRescheduled, provider against the published schema
tests/contract/notify-consumer.spec.ts      the field-notify API this slice consumes
tests/e2e/reschedule.e2e.spec.ts            @covers AC-014a — POST /jobs/{id}/slot through the real interface
```

The slot-overlap query had an unknown shape, so it was spiked as a throwaway, the index confirmed, the spike deleted, and the query then driven by the integration test.

One edge the brief did not cover: rescheduling a job to the slot it already holds. Two engineers would settle it the same way (an idempotent no-op that emits no event), so it was decided, written into the functional spec as `AC-014e`, added to the brief's `behavior` row, and covered by a unit test in the same change.

## Report

T-014 is done and pushed; the deploy's smoke check passed.

| Check | Result |
|---|---|
| project gate (format · lint · types · unit · fitness) | green |
| integration tier | green, 0 skipped |
| `check_task.py spec --task T-014` | green — 5 of 5 criteria covered |
| e2e against the deployed environment | written, not run — no CI job runs it under `trunk` |

One spec change to know about: `AC-014e` (same-slot reschedule is a no-op) is new in the functional spec. Nothing is blocked.
