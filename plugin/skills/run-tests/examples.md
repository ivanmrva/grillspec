# run-tests — worked example

Gating **T-014 — Reschedule a booked job**. Running the suite *is* the verification: each acceptance criterion proven at the right level, coverage and mutation-adequacy met, one verdict line emitted.

Each `AC-` is checked at the level its nature demands — a user-observable outcome through the real interface, a persistence rule against a real DB, a pure rule as a unit test:

| AC | nature | level run | asserts |
|---|---|---|---|
| AC-014a happy | user-observable | **e2e** through `POST /jobs/{id}/slot` | resulting state: job slot = new time, old slot released |
| AC-014b owning-branch | pure domain rule | unit | rejection `not-owning-branch` |
| AC-014c lead-time | pure domain rule | unit | rejection `lead-time-violated` (incl. boundary: exactly 2h) |
| AC-014d slot-taken | persistence / concurrency | **integration** (real Postgres) | rejection `slot-taken` under a held slot |

EVT-JobRescheduled flows through the **real outbox path** — a real worker drains it, the observable publish is asserted with **poll-with-timeout (no sleep)** on a controlled clock; re-delivery asserted idempotent. Assertions are on observable outcome (state / emitted event), never on interactions. Every AC test was confirmed able to fail (mutated the rule, watched it go red).

Coverage 94% vs 90% target — pass. **Mutation score on the changed domain logic (job.reschedule): 88% vs 85% target** — the surviving mutant was the `>= 2h` boundary flipping to `>`; AC-014c's boundary case already kills it, so no real gap. Async retry/idempotency/dead-letter paths all exercised.

```
VERDICT: PASS
```
Suite green · every AC exercised at the right level · coverage + mutation targets met. (Had AC-014a been mock-only instead of e2e, or a surviving mutant uncovered → `VERDICT: FAIL`, back to implementation.)
