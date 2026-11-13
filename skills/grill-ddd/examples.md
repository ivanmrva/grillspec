# grill-ddd — worked example

Illustrative: it shows the shape of the output, not a list to fill. A field-service domain, modelled event-first. The user never hears DDD jargon.

> **Agent:** When a repair is booked, who can later change the appointment time — only dispatch, or the technician too? *(I'd expect dispatch owns scheduling and the tech only reports status.)*
> **User:** Dispatch owns it; the tech just checks in and out.
> **Agent:** Does a job ever move between branches mid-repair, or stay with the branch that booked it? *(I'd default to: stays.)*
> **User:** Stays with the booking branch.

The check-in is the pivotal event that seams Scheduling from FieldWork.

## Output — `strategic/context-map.md`
```mermaid
flowchart LR
  Scheduling -- "Customer-Supplier · upstream ▸ publishes EVT-203 JobCheckedIn" --> FieldWork
```

## Output — `tactical/scheduling/aggregates.md`
**AGG-201 Job** (root: Job)
- invariants:
  - INV-201 OwningBranchFixed — the owning branch is fixed at creation
  - INV-202 NoDoubleBookedTech — a technician holds at most one job per time slot (cross-aggregate; restored by POL-201)
- transaction boundary: the job only; technician availability is a separate aggregate
- commands: CMD-201 ScheduleJob · CMD-202 RescheduleJob · CMD-203 CheckIn · CMD-204 CompleteJob
- events: EVT-201 JobScheduled · EVT-202 JobRescheduled · EVT-203 JobCheckedIn · EVT-204 JobCompleted
- size: one job and its line items; bounded, low contention

| from | trigger | to | guard |
|---|---|---|---|
| (initial) | CMD-201 ScheduleJob | Scheduled | slot is free |
| Scheduled | CMD-202 RescheduleJob | Scheduled | not checked in |
| Scheduled | CMD-203 CheckIn | CheckedIn | — |
| CheckedIn | CMD-204 CompleteJob | Completed | — |
| Completed | — | (terminal) | — |

## Output — `tactical/scheduling/policies.md`
- POL-201 ReserveSlot — whenever EVT-201 JobScheduled then CMD-210 ReserveSlot on the technician calendar. Scheduling can break the no-double-booking rule; the reservation repairs it, so the rule holds eventually and outside the job's transaction.

## Output — `tactical/scheduling/value-objects.md`
- VO-201 Slot `{ start, durationMinutes }` — immutable, equal by value; `start` must fall on the branch's working calendar
- VO-202 JobId — a typed id, so a job id cannot be passed where a technician id is expected

## Output — `strategic/hotspots.md`
`HOT-001 · Scheduling · can one job be split across two technicians? · open`

No repository, factory or domain-service catalogue was written: the domain has none worth naming beyond one repository per aggregate.
