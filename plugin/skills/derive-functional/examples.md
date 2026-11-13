# derive-functional — worked example

Illustrative: it shows the shape, not required content.

The domain model carries `CMD-RescheduleJob`, invariant `INV-Job-LeadTime` (no move to a slot less than 2h away) and policy `POL-Scheduling-Owner` (only the booking branch's dispatcher may move a job). They project into one use-case: its happy path and the rejections the rules already entail.

## Output
`functional-spec/use-cases.md`

### UC-014 — Reschedule a booked job
- actor: Dispatcher (booking branch)
- trigger: submits a new slot for an existing job
- outcome: job moved to the new slot; original slot released
- maps-to: CMD-RescheduleJob
- flows: happy path · permission denied · invalid input (lead time) · conflict

Acceptance criteria:
- AC-014a (happy) — Given a booked job owned by the dispatcher's branch and a free slot at least 2h away, When the dispatcher submits that slot, Then the job moves to it and the original slot is released.
- AC-014b (permission denied) — Given a booked job and a dispatcher from a branch that did not book it, When the dispatcher submits a new slot for the job, Then the reschedule is rejected with `not-owning-branch` and the job keeps its slot. ← POL-Scheduling-Owner
- AC-014c (invalid input) — Given a booked job and a new slot that starts in less than 2h, When the job's dispatcher submits that slot, Then the reschedule is rejected with `lead-time-violated`. ← INV-Job-LeadTime
- AC-014d (conflict) — Given a booked job and a target slot already held by another job, When the dispatcher submits that slot, Then the reschedule is rejected with `slot-taken`.

Deferred (`at-task`): what a customer with an SMS confirmation is told when the slot moves. No domain rule covers it, so it is raised against the domain model.
