# conformance-review — worked example

The post-task review of the **T-014** code against our spec, scope `changed` (the slice + its blast radius). Lens A (conformance) is blocking; Lens B (design health) is advisory. Architecture is checked first — it's where shortcuts creep in on a re-run to green.

**Lens A — architecture first.** Dependency direction & acyclicity hold for the domain and repository. But the new code reaches the field-notification system the wrong way:

> The reschedule application-service imports `fieldwork/notify/SmsClient` **directly** to send the confirmation. That crosses the Scheduling→FieldWork context boundary against the published-contract rule, and the service's declared `role: application-service` (depends inward only) now depends on a sibling context's *internal* adapter — its real dependencies contradict its role direction. A green test masked it.

Fix stays inside the boundaries: emit `EVT-JobRescheduled` and let FieldWork consume it; the direct import is deleted, not the boundary bent. (Spec is upstream truth — not edited to match the code.)

**Traceability** (`delivery/verification/traceability.md`):

| spec ID | T- | code | test | pass |
|---|---|---|---|---|
| CMD-RescheduleJob | T-014 | `scheduling/app/reschedule-job-service.ts` | `tests/unit/job.reschedule.spec.ts` | ✓ |
| INV-Job-LeadTime | T-014 | `scheduling/domain/job.ts` | `tests/unit/job.reschedule.spec.ts::AC-014c` | ✓ |
| EVT-JobRescheduled | T-014 | `scheduling/app/reschedule-job-service.ts` | `tests/contract/job-rescheduled.evt.spec.ts` | ✓ |
| API-RescheduleJob | T-014 | `scheduling/api/reschedule.route.ts` | `tests/e2e/reschedule.e2e.spec.ts` | ✓ |

```
VERDICT: FAIL — Scheduling→FieldWork context boundary crossed (direct SmsClient import;
role/direction contradiction). Back to implementation; re-review the fix.
```

**Lens B (advisory, never blocks):** the slot-overlap check is a shallow module (interface ≈ implementation) — candidate to deepen behind the repository once a second reservation strategy appears; not now (one adapter = hypothetical seam). Logged, doesn't affect the verdict.
