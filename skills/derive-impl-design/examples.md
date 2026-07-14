# derive-impl-design — worked example

Designing one module behind the *reschedule-a-job* command — produced JIT for a complex slice, the last layer before code, no implementation written.

**Given by the architecture (not re-decided here)** — the module map already fixed this module's role, dependency direction, and seam interface:

```
module: reschedule-job-service
role: application-service     dep-direction: inward only (→ domain AGG-Job; out via driven-ports)
seam interface (the test surface, fixed in the architecture):
  reschedule(jobId: JobId, newSlot: Slot, actor: DispatcherId) -> Result<JobRescheduled, RescheduleError>
```

This slice is flagged `design-first` (real concurrency + a cross-system notification), so we design the **internals behind that seam** — a deep module: much behavior, the small interface unchanged.

## Output
`delivery/impl-design/reschedule-job-service.md`

```
implements MOD-07 (reschedule-job-service) · serves T-031 (reschedule a job)
algorithm (sketch)
  1. load Job via JobRepository (driven-port)         5. publish EVT-JobRescheduled
  2. job.reschedule(newSlot, actor)  ← aggregate rule     (outbox, same tx as persist)
  3. on Err → return propagated
  4. persist via repository
concurrency
  optimistic lock on Job.version; retry-once on stale read; load→mutate→persist→publish atomic
  (publish via the outbox in the same tx — no dual-write); cancellation: none (single short tx)
errors  (taxonomy + each designed-out | masked | propagated)
  - NotOwningBranch     designed-out — the aggregate rejects; the typed error is propagated
  - LeadTimeViolated    propagated — surfaced to the caller as-is (maps to AC rejection)
  - SlotTaken           propagated — from the slot reservation, returned unchanged
  - NotifierUnavailable masked-at-boundary — publish is via the outbox, so a down notifier never
                        fails the command; the event drains on recovery
```
No seam invented for the notifier beyond the one outbound port the architecture fixed — a second transport would justify a second adapter, not yet (JIT: the second consumer reveals the real seam). A needed interface change would be raised as a **gap to the architecture**, not patched here.
