# grill-ddd — worked example

Modelling a field-service domain **event-first** — no DDD jargon spoken to the user.
> **Claude:** When a repair is booked, who can later change the appointment time — only dispatch, or the technician too? *(I'd expect dispatch owns scheduling; the tech only reports status.)*
> **User:** Dispatch owns it; the tech just checks in/out.
> **Claude:** Does a *Job* ever move between branches mid-repair, or stay with the branch that booked it? *(I'd default to: stays.)*
> **User:** Stays with the booking branch.

The check-in is the **pivotal event** that seams **Scheduling** from **FieldWork**.

## Output — `strategic/context-map.md`
```mermaid
flowchart LR
  Scheduling -- "Customer-Supplier · upstream ▸ publishes EVT-JobScheduled" --> FieldWork
```

## Output — `strategic/event-flow.md` (Scheduling)
`EVT-JobRequested ⟵ CMD-RequestJob` → `EVT-JobScheduled ⟵ CMD-ScheduleJob` → **`EVT-JobCheckedIn`** *(pivotal — hands the Job off to FieldWork)* → `EVT-JobCompleted ⟵ CMD-CompleteJob`

## Output — `tactical/scheduling/aggregates.md`
```
AGG-Job   (root: Job)
  invariants:
    - the owning branch is fixed at creation (never reassigned)
    - one Technician holds at most one Job per time-slot   (cross-aggregate → policy below)
  state model:  Requested → Scheduled → CheckedIn → Completed
                guards: CheckIn only from Scheduled · Complete only from CheckedIn · no Reschedule after CheckedIn
  transaction boundary: the Job only — Technician availability is a separate aggregate
  commands: CMD-ScheduleJob · CMD-RescheduleJob · CMD-CheckIn · CMD-CompleteJob
  events:   EVT-JobScheduled · EVT-JobRescheduled · EVT-JobCheckedIn · EVT-JobCompleted
  size: one Job + its line-items — bounded, low contention; small by design
  cross-aggregate policy (eventual consistency):
    whenever EVT-JobScheduled then CMD-ReserveSlot  → AGG-TechnicianCalendar
    (the scheduling event can break the no-double-book rule; the reservation command repairs it)
```

## Output — `tactical/scheduling/value-objects.md`
- **VO-Slot** `{ start, durationMinutes }` — immutable, equal by value; validates `start` falls on the branch's working calendar
- **VO-Money** `{ amountMinor, currency }` — no floats; arithmetic only within one currency
- **VO-JobId** — a typed id, not a bare UUID/string, so a `JobId` can't be passed where a `TechnicianId` is expected

## Output — `strategic/hotspots.md`
`HOT-001 · Scheduling · can one Job be split across two technicians (parallel parts)? — open; blocks the reschedule rule`

Recorded: two contexts seamed at the pivotal check-in; **one typed, directed relationship** (Customer-Supplier, Scheduling upstream); **AGG-Job as a single block** — root · invariants · **state model with transition guards** · tx-boundary · commands · events · size — its cross-aggregate invariant naming a **`whenever EVT-… then CMD-…`** policy; **value objects made first-class** (Slot/Money/typed-Id carry their own rules); a hotspot left open, not papered over. Every command produces an event; the double-book rule holds **eventually** via the reservation policy, not inside the Job transaction.
