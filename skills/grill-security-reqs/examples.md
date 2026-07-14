# grill-security-reqs — worked example

Setting the authorization rule for *reschedule-job* and the matching tampering threat.

> **Claude:** Default-deny: who may reschedule a job? If any dispatcher can move any branch's job, that's a cross-tenant hole. *(I'd allow only the dispatcher whose branch booked it — a tenant predicate, not a flat role grant.)*
> **User:** Only the booking branch's dispatcher. A tech can't reschedule at all.
> **Claude:** Then the risk is a dispatcher tampering with another branch's schedule by guessing a job-id — I'll log every reschedule append-only so it's at least attributable. Accept or control?
> **User:** Control it — enforce the predicate and keep the audit trail.

Recorded: one default-deny authz rule carrying a tenant predicate, plus the tampering/repudiation control.

## Output
`requirements/security/authorization.md`

**SEC-002 — Reschedule job**
- actor × command: Dispatcher × RescheduleJob → **allow** if `job.bookingBranch == actor.branch`; else **deny**
- Technician × RescheduleJob → **deny** (unspecified = forbidden)
- model shape: relationship-based (ownership predicate) — decided in `adr/ADR-SREQ-001.md`

`requirements/security/threat-model.md`
- id: THR-002 · asset: Job schedule · boundary: authenticated-dispatcher → Scheduling
  - threat (tampering): dispatcher mutates another branch's job by guessing job-id
  - control: enforce SEC-002 tenant predicate at command handler
- id: THR-003 · asset: Job schedule · same boundary
  - threat (repudiation): dispatcher denies making a disruptive reschedule
  - control: append-only, tamper-evident reschedule audit log · retention 24 months
- ASVS target: L2 · OWASP Top-10: 2021 edition
- threat actor: negligent/malicious insider (dispatcher) — capability: valid session; motive: load-shifting
