---
name: grill-growth
description: >-
  Pin the post-launch growth model — activation, retention and referral, an experiment backlog,
  and the analytics events the product must emit to measure it; closes the loop from launch back
  to discovery. Loads the shared grill engine.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-growth

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Growth & analytics (post-launch loop)** — the growth model and the events that measure it.

## Method
- Model **growth loops** alongside the funnel — trigger → action → output → reinvested input — and **name the primary loop** that compounds acquisition.
- Type **activation** as a bar: event + count + window (e.g. "created ≥3 projects within 7 days"), paired with a **time-to-value** target.
- Define the **retention curve / cohorts** and treat the **plateau** as the durable-growth check; for high-frequency products also pin a **stickiness ratio** (DAU/MAU or equivalent).
- Pin the **event-taxonomy naming convention** — object-action, controlled vocabulary — before listing events.

## Rules
- **post-launch and parallel** — don't gate the build on it; but its *analytics events* must reach the task breakdown so instrumentation is built in, not bolted on — **concretely: each `AEV-` event lands in the emitting slice's `obs` dimension by id** (with the `EXP-` it serves), which the Verification Record's `obs` gate row then holds to an emission assertion; an `AEV-` that reaches no task's `obs` cell will never be emitted (lint warns on it)
- activation + retention are defined against the north-star; the experiment backlog has ≥1 `EXP-` carrying a metric
- **activation** is a typed bar (event + count + window) with a time-to-value target — never an adjective
- retention is a **cohort curve** whose plateau is the durable-growth check (+ a stickiness ratio when high-frequency)
- every experiment declares an **MDE**, **power/alpha**, derived **sample size**, **min-runtime**, a **guardrail metric**, and a **stop-rule** — no peeking unless a sequential method is declared
- events follow the pinned **object-action** controlled vocabulary and each carries an **owner**

## Output
**Stable IDs** (bare type prefix, ID = the leading table column / row key): `EXP-` a growth experiment · `AEV-` an analytics event (the instrumentation contract — an event is referenceable by id, so a task's `obs` cell, an experiment, and a rename all trace to the same row).
Written under `commercial/growth/`:

| File | Captures | Format |
|---|---|---|
| `growth-model.md` | acquisition → activation → retention → referral/revenue (tied to north-star) + **named primary growth loop** (trigger→action→output→reinvested input) + activation bar (event·count·window) + time-to-value + retention-curve/cohorts (plateau · stickiness) + leading indicators | funnel · loop · fields |
| `experiments.md` | experiment backlog — id EXP-NNN | hypothesis · primary metric · MDE · power/alpha · sample size · min-runtime · guardrail metric · stop-rule |
| `analytics-events.md` | events/properties to track — id `AEV-NNN` per event (object-action naming, with consent/tracking classification, the `EXP-` it serves) + cohort/funnel definitions | **`AEV-` id** · event · properties · classification · serves(`EXP-`) · owner |

ADRs → `adr/ADR-GRW-NNN.md`
Consumes: the compliance obligations / data classification (each event carries its consent/tracking class).

## Excludes
metric *targets* (→ the success metrics / goals) · the telemetry *plumbing* (→ the architecture) · pricing experiments' model (→ the commercial model)

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
