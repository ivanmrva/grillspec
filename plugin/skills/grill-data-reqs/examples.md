# grill-data-reqs — worked example

Governing the *customer contact record* captured when a repair is booked.

> **Claude:** This holds name, address and phone — that's personal data. What's the deletion trigger and TTL: do we keep it forever, or drop it once the warranty window closes? *(I'd peg retention to the obligation, not "a while" — say 24 months after job completion, matching the warranty period.)*
> **User:** 24 months after the job closes, then purge.
> **Claude:** And where does it physically live versus whose law governs access — same answer, or split? *(I'd put storage in eu-central-1 but flag that the parent co. is US-incorporated, so sovereignty ≠ residency.)*
> **User:** Stored in Frankfurt; parent is US — so yes, US can be compelled.

Recorded: one governed data-class, personal, with split residency/sovereignty and a TTL+trigger.

## Output
`requirements/data/data-classes.md`

**DATA-003 — Customer contact record**
- category: customer master / personal
- classification: PII
- ownership: Branch Operations (data steward), per booking branch
- consent: lawful basis = contract performance · granularity = contact-for-service vs. marketing (separate) · withdrawal = marketing opt-out self-serve · re-consent = on marketing-purpose change
- retention: TTL 24 months · deletion trigger = job closed → purge (warranty window)
- residency: eu-central-1 (Frankfurt)
- sovereignty: US — parent company US-incorporated, subject to lawful compulsion (flag: needs counsel)
- lineage: origin = booking flow (Scheduling) · derivation = none · downstream = dispatch SMS, invoicing
- volume/growth: ~250k records, +8k/mo · access = read-heavy, queried by phone + job-id
- integrity: mutable; durability no-loss
- data-quality (value-bearing): accuracy, validity (phone format), completeness
