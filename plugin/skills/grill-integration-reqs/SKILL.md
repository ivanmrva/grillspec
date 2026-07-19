---
name: grill-integration-reqs
description: >-
  Per external boundary, elicit the qualities and obligations of each exchange in detail — direction, interaction-style, volumes, latency, SLA, delivery guarantee + idempotency/ordering/retry/DLQ/replay, failure/degradation behaviour, reconciliation, auth. Use when the boundary roster already exists and you need each seam specified. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-integration-reqs

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Integration requirements** — the qualities/obligations of each external exchange, not the boundary roster itself.

## Rules
- every external seam covered or marked N/A
- **every seam file is anchored to its `IF-` id** — the file opens by citing the system-context interface it elicits (`elicits IF-NNN`), so the seam's qualities are ID-reachable: a task implementing the seam cites that `IF-` in its `integration` dimension, which mints the obligation row (`real-path integration test incl. failure/degradation path`) the Verification Record holds it to, and lint warns on an `IF-` no seam file or task ever references. Prose qualities with no `IF-` anchor are unreachable by every downstream gate
- each seam states **direction + what-flows + SLA + failure/degradation behaviour + contract owner** (us/them/a standard) **+ interaction-style** (sync request-reply · async messaging · webhook push · poll · stream)
- **what is exchanged in domain vocabulary** (which aggregates/events/facts) **+ the semantic/field mapping** (our term ↔ their term) for ACL seams
- volume/shape: throughput · batch/stream · payload order · peak · **the external system's rate limits/quotas** · **a backpressure expectation where throughput warrants**
- **integration SLA**: freshness/latency · availability · **delivery guarantee — at-least-once / at-most-once / effectively-once (at-least-once + idempotent); never claim "exactly-once"** · **failure/degradation expectation**
- **per-seam delivery contract**: idempotency key + dedup window · ordering guarantee + partition key · retry/backoff expectation · DLQ/poison-message handling · replay/backfill-after-fix
- **reconciliation is a bar**: cadence · comparison key · gap-handling (what closes a detected drift)

## Output
Written under `requirements/integration/`:

One file per external boundary — add files as boundaries are enumerated.

| File | Captures | Format |
|---|---|---|
| `<boundary>.md` | one file per external boundary/seam (named after it): **`elicits IF-NNN`** (the system-context interface this seam specifies — the ID anchor tasks and lint reach it by) · direction · interaction-style · what-flows · volume · backpressure · latency · SLA · delivery guarantee · idempotency key + dedup window · ordering + partition key · retry/backoff · DLQ/poison · replay/backfill · reconciliation (cadence · comparison key · gap-handling) · owner · auth | typed fields: interaction-style · volume · latency · SLA · delivery guarantee · idempotency · ordering · retry/backoff · DLQ · replay · reconciliation · owner · auth |

ADRs → `adr/ADR-IREQ-NNN.md`
Consumes: the system context's interface inventory (the boundary roster), cross-checked against the domain context-map's external seams.

## Excludes
which systems exist + what crosses + its meaning, and the **protocol category** (→ the system context) · the **API/event schemas & their versioning** (→ the API contracts) · the **transport mechanism** — wire protocol, message broker, and the retry/circuit-breaker resilience *implementation* (→ the architecture; the broker is provisioned by infra). This area states each seam's delivery *requirement* (idempotency · ordering · retry/backoff · DLQ · reconciliation); building the mechanism that meets it is the architecture's job.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
