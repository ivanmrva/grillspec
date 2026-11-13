# grill-security-reqs — worked example

Illustrative: it shows the shape of the output, not a list to fill. The rule is for rescheduling a job in a multi-branch product on the `standard` profile.

> **Agent:** Default-deny: who may reschedule a job? If any dispatcher can move any branch's job, that is a cross-tenant hole. *(I'd allow only the dispatcher whose branch booked it: a tenant predicate, not a flat role grant.)*
> **User:** Only the booking branch's dispatcher. A tech cannot reschedule at all.
> **Agent:** Then the risk is a dispatcher changing another branch's schedule by guessing a job id. Accept it, or control it?
> **User:** Control it. Enforce the predicate and keep an audit trail.

## Output — `authorization.md`
| SEC-id | actor | command | decision | condition |
|---|---|---|---|---|
| SEC-002 | Dispatcher | CMD-202 | allow | `job.bookingBranch == actor.branch` |
| SEC-003 | Technician | CMD-202 | deny | — |

Model shape: relationship-based (ownership predicate), decided in ADR-SREQ-001.

## Output — `threat-model.md`
Verification level: OWASP ASVS L2. Threat actor: a negligent or malicious dispatcher with a valid session, shifting load to another branch.

| THR-id | asset | threat | boundary | control / accepted-risk | owner |
|---|---|---|---|---|---|
| THR-002 | job schedule | tampering: changes another branch's job by guessing its id | dispatcher → Scheduling | SEC-002 | Scheduling |
| THR-003 | job schedule | repudiation: denies a disruptive reschedule | dispatcher → Scheduling | append-only reschedule audit log, kept 24 months (ADR-SREQ-002) | Scheduling |

The threats every web application shares are covered by the ASVS level and are not listed.
