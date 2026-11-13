# grill-quality — worked example

Illustrative: it shows the shape of the output, not a list to fill. The wish is "checkout should feel fast and never lose an order", for an e-commerce checkout on the `standard` profile.

> **Agent:** "Fast" needs a number at a load. At what concurrent-checkout volume must p95 hold — Black-Friday peak or a normal Tuesday? *(I'd set the bar at peak; a Tuesday number will not protect you when it matters.)*
> **User:** Peak. We have hit about 3,000 concurrent checkouts.
> **Agent:** And "never lose an order" — is that zero data loss (RPO 0) on a placed order, even if a node dies mid-write? *(That forces synchronous durability and pushes against the latency target.)*
> **User:** Yes, a placed order is sacred. RPO 0. The cart can be best-effort.

## Output — `nfrs.md`
| id | attribute | stimulus | response (number @ point) | enforced-by | ASR? |
|---|---|---|---|---|---|
| NFR-014 | Performance | place-order at 3,000 concurrent checkouts | p95 ≤ 800 ms server-side; throughput ≥ 250 orders/s | gate (load test) | ASR-014 |
| NFR-021 | Reliability (recoverability) | node failure mid-write of a placed order | RPO = 0; RTO ≤ 90 s; dr-tier warm-standby | infra | ASR-021 |
| NFR-022 | Availability | checkout service, rolling month | ≥ 99.95% (≤ 21.9 min/month); dr-tier warm-standby | infra | — |
| NFR-030 | Accessibility | keyboard-only user completes checkout | current WCAG at AA, zero blockers | gate (axe scan) | — |
| NFR-037 | Security level | dependency and container scan | OWASP ASVS L2; criticals patched ≤ 7 days | gate | — |

## Output — `asrs.md`
**ASR-014** (← NFR-014) — *Source:* shopper · *Stimulus:* taps "Place order" · *Artifact:* checkout-order service · *Environment:* peak, 3,000 concurrent · *Response:* order persisted and confirmation rendered · *Measure:* p95 ≤ 800 ms, ≥ 250 orders/s.

**ASR-021** (← NFR-021) — *Source:* infrastructure · *Stimulus:* primary database node lost during commit of a placed order · *Artifact:* order store · *Environment:* normal operation · *Response:* failover with no acknowledged order lost · *Measure:* RPO 0, RTO ≤ 90 s.

Conflict: NFR-021 (RPO 0 needs synchronous durability) pulls against NFR-014's 800 ms p95. Settled in ADR-QUAL-003: replicate only the placed-order write synchronously, the cart asynchronously.

Five targets shape this design, so the file has five rows; safety and co-existence do not stress a checkout and get none.
