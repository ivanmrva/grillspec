# derive-functional — worked example

Projecting the *reschedule-appointment* command (domain rule: only the booking branch's dispatcher may move a job, and not within 2h of the slot).

The domain model carries `CMD-RescheduleJob`, invariant `INV-Job-LeadTime` (no move <2h before slot) and policy `POL-Scheduling-Owner` (booking-branch dispatcher only). These project straight into one use-case with its happy path and the rejections the rules already entail — no new rules invented here.

Residual product-behavior edge found while projecting: *what happens to a customer who already received an SMS confirmation when the slot moves?* No invariant speaks to it → recorded as a **Deferred** gap (`at-task`), not authored here.

## Output
`requirements/functional/use-cases.md`

**UC-014 — Reschedule a booked job**
- actor: Dispatcher (booking branch)
- trigger: dispatcher submits a new slot for an existing `Job`
- outcome: job's slot updated; original slot released
- maps-to: CMD-RescheduleJob
- flows: happy path · permission-denied · invalid-input (lead-time) · conflict

  - **AC-014a** (happy) — *Given* a job owned by the dispatcher's branch and the new slot is ≥2h away, *When* they submit it, *Then* the job's slot is updated to the new time.
  - **AC-014b** (permission-denied) — *Given* a dispatcher whose branch did not book the job, *When* they submit a new slot, *Then* the request is rejected with `not-owning-branch`. *(← POL-Scheduling-Owner)*
  - **AC-014c** (invalid-input / lead-time) — *Given* the new slot is <2h from now, *When* they submit it, *Then* the request is rejected with `lead-time-violated`. *(← INV-Job-LeadTime)*
  - **AC-014d** (conflict) — *Given* the target slot is already held by another job, *When* they submit it, *Then* the request is rejected with `slot-taken`.

Deferred (`at-task`): customer-notification on slot change — no domain rule yet; raise to domain model before projecting.
