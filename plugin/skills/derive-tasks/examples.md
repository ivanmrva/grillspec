# derive-tasks — worked example

A single implementation-final task manifest:
```
T-014 | phase: MVP | Pay an order (vertical slice)
behavior:    UC-014 · AC-014a, AC-014b
domain:      AGG-Order · CMD-Pay · EVT-OrderPaid · INV-Order-total>=0
data:        DATA-03 (payment record; retain 7y)
api:         API-Pay  (POST /orders/{id}/payments)
ux:          ux-reqs#pay-flow → prototype: prototypes/ui/pay.html (confirm dialog · spinner · receipt · error states)
a11y:        keyboard tab→confirm · focus trap in dialog · WCAG SC 2.4.7 (focus visible), SC 3.3.1 (error identified)
security:    SEC-03 (only Owner/Billing may pay) · validate amount > 0
nfr:         ASR-002 (p95 < 300ms)
integration: PSP-Stripe (charge)
placement:   billing context · src/billing/{api,app,domain,infra}
design:      inline  (CRUD-shaped over the aggregate — no hard algorithm/concurrency, so no design-first pass)
tests:       unit(domain) + contract(API-Pay) + e2e(AC-014a); fixture: seeded order
depends:     T-002 (order aggregate)
outcome:     a buyer pays an order and sees a receipt
DoD:         AC green · in-boundary · CI green · traceability updated
```
Every dimension resolved (or N/A) → the agent can implement with zero ambiguity. `design: inline` here because the slice is CRUD-shaped; a slice with a **hard algorithm · real concurrency · a cross-context saga** would be `design: design-first`, and its module internals get a JIT impl-design pass before coding. If the slice UX weren't yet defined, this task is *not* final — derive-and-ask the flow (and generate its prototype screen), record it here, then ship.
