# grill-quality — worked example

Turning "checkout should feel fast and never lose an order" into measurable NFRs for an e-commerce checkout.
> **Claude:** "Fast" needs a number *at a load*. At what concurrent-checkout volume must p95 hold — Black-Friday peak or a normal Tuesday? *(I'd set the bar at peak; a Tuesday number won't protect you when it matters.)*
> **User:** Peak. We've hit ~3,000 concurrent checkouts.
> **Claude:** And "never lose an order" — is that zero-data-loss (RPO 0) on a placed order, even if a node dies mid-write? *(That forces synchronous durability and pushes against the latency target — a real conflict.)*
> **User:** Yes, a *placed* order is sacred. RPO 0. The cart can be best-effort.

## Output — `nfrs.md`
| id | attribute | stimulus | response (number @ point) | enforcement | ASR? |
|---|---|---|---|---|---|
| NFR-014 | Performance | place-order at 3,000 concurrent checkouts | p95 ≤ 800 ms server-side; throughput ≥ 250 orders/s | gate (load test in CI) | ASR-014 |
| NFR-021 | Reliability (recoverability) | node failure mid-write of a placed order | RPO = 0; RTO ≤ 90 s | infra | ASR-021 |
| NFR-022 | Availability | checkout service, rolling month | ≥ 99.95% (≤ 21.9 min/mo) | infra | — |
| NFR-030 | Interaction-capability (accessibility) | keyboard-only user completes checkout | current WCAG at AA, zero blockers | gate (axe in CI) | — |
| NFR-037 | Security level | dependency + container scan | OWASP ASVS L2; criticals patched ≤ 7 days | gate | — |

## Output — `asrs.md`
**ASR-014** (← NFR-014) — *Source:* shopper · *Stimulus:* taps "Place order" · *Artifact:* checkout-order service · *Environment:* peak, 3,000 concurrent · *Response:* order persisted + confirmation rendered · *Measure:* p95 ≤ 800 ms, ≥ 250 orders/s.
**ASR-021** (← NFR-021) — *Source:* infrastructure · *Stimulus:* primary DB node loss during commit of a placed order · *Artifact:* order store · *Environment:* normal operation · *Response:* failover with no acknowledged-order lost · *Measure:* RPO 0, RTO ≤ 90 s.

**Conflict surfaced:** NFR-021 (synchronous, RPO 0) pulls against NFR-014's 800 ms p95 — synchronous replication adds write latency. Resolution recorded as ADR-QUAL-003: sync-replicate only the placed-order write, async for cart.

Recorded: tree walked across performance / reliability / security-level / interaction-capability — moot branches (safety, co-existence) marked skipped; every NFR a number + point + enforcement category; two ASRs as full 6-part scenarios; one consistency↔latency conflict named. No mechanism (replica/queue) prescribed — that's the solution's job.
