---
name: grill-integration-reqs
description: >-
  Specify what each external seam must guarantee: direction, interaction style, volumes, SLA,
  delivery guarantee with idempotency, ordering and retry, failure behaviour and reconciliation.
  Use once the boundary interfaces are listed and a seam carries money, a delivery guarantee or
  a quota.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-integration-reqs

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Integration requirements** — the qualities/obligations of each external exchange, not the boundary roster itself.

## Depth by profile
| Profile | What the interview captures |
|---|---|
| `lite` | not a separate area. |
| `standard` | a full seam file only for a seam that moves money, needs a delivery guarantee (a lost or duplicated message has a consequence), or sits under a hard external quota. Every other seam is one row in `seams.md`. |
| `regulated` | a full seam file for every external seam. |

## Rules
- Cover every external seam the system context lists, or mark it N/A with the reason. A product with no external seam writes `seams.md` as one line, `N/A — <why>`.
- Every seam is anchored to the interface it elicits. A seam file opens with `elicits IF-NNN`, and a `seams.md` row carries the id in its `elicits` column. The id is how the task that builds the seam, and the coverage check, reach its qualities; prose with no `IF-` anchor is unreachable.
- A seam states its direction, what flows, its SLA, its failure and degradation behaviour, the contract owner (us · them · a standard) and its interaction style.
- What flows is stated in domain vocabulary: which aggregates, events or facts. A seam behind an anti-corruption layer adds the term mapping (our term ↔ their term).
- Volume and shape: throughput · batch or stream · payload order · peak · the external system's rate limits and quotas · a backpressure expectation where the throughput warrants one.
- The integration SLA: freshness or latency · availability · delivery guarantee · the failure and degradation expectation.
- The delivery guarantee is at-least-once, at-most-once or effectively-once (at-least-once plus idempotent). No network can promise exactly-once, so the spec does not claim it.
- The delivery contract: idempotency key and dedup window · ordering guarantee and partition key · retry/backoff expectation · dead-letter and poison-message handling · replay or backfill after a fix.
- Reconciliation is a bar: cadence · comparison key · gap handling (what closes a detected drift).

## Output
Written under `requirements/integration/`:

| File | Captures | Format |
|---|---|---|
| `<boundary>.md` | one file per seam that gets the full specification, named after the boundary | `elicits IF-NNN`, then typed fields: direction · interaction-style · what-flows · volume · backpressure · latency · SLA · delivery-guarantee · idempotency · ordering · retry/backoff · DLQ · replay · reconciliation · owner · auth |
| `seams.md` | every other external seam, one row each | table: seam · elicits · direction · interaction-style · what-flows · on-failure |

Two fields are closed sets, written as the exact tokens so the consistency check can compare them: `interaction-style` ∈ sync request-reply / async messaging / webhook push / poll / stream, and `delivery-guarantee` ∈ at-least-once / at-most-once / effectively-once.

In `seams.md` the seam name leads the row and the `IF-` id sits in the `elicits` column. The interface is defined in the system context, and an id in the leading cell would read as a second definition.

ADRs → `adr/ADR-IREQ-NNN.md`
Consumes: the system context's interface inventory (the boundary roster), cross-checked against the external seams on the domain context map.

## Excludes
which systems exist, what crosses and what it means, and the protocol category (→ the system context) · the API and event schemas and their versioning (→ the API contracts) · the transport mechanism — wire protocol, message broker, and the retry or circuit-breaker implementation (→ the architecture). This area states each seam's delivery requirement; building the mechanism that meets it is the architecture's job.

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
