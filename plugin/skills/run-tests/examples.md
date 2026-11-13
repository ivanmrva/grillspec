# run-tests — worked example

Illustrative. Slice scope, for T-014 "Reschedule a booked job".

```
VERDICT: PASS
```

The project gate and the integration tier are green with nothing skipped, and `check_task.py spec --task T-014` is green: all four criteria have a `@covers` test. Each criterion is tested at the level its nature needs:

| Criterion | Nature | Level run | Asserts |
|---|---|---|---|
| AC-014a happy path | user-observable | e2e through `POST /jobs/{id}/slot` | the job holds the new slot and the old slot is released |
| AC-014b owning branch | pure domain rule | unit | rejected as `not-owning-branch` |
| AC-014c lead time | pure domain rule | unit | rejected as `lead-time-violated`; exactly 2h is accepted |
| AC-014d slot taken | persistence, concurrency | integration, real Postgres | rejected as `slot-taken` while another job holds the slot |

The `EVT-JobRescheduled` event goes through the real outbox: a worker drains it, the publish is asserted by polling with a timeout under a controlled clock, and a second delivery changes nothing. Retry and the dead-letter path are exercised.

The gate's bars are met: 94% branch coverage against 90%, and 88% mutation score on the changed domain logic against 85%. The one surviving mutant flips `>= 2h` to `> 2h` in a log message, not in the rule; the boundary case in AC-014c kills the rule mutation.

What ran where: unit, integration and contract locally; the e2e against the preview environment. Nothing was left unrun.

Had AC-014a been covered only by a mocked handler test, the first line would read `VERDICT: FAIL — AC-014a is user-observable and has no test through the real interface`, and the slice would go back to implementation.
