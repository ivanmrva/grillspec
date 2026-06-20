---
name: grill-growth
description: >-
  Pin the post-launch growth model — activation/retention/referral, an experiment backlog, and the analytics events the product must emit to measure it. Use when you need a growth model plus its instrumentation; closes the loop from launch back to discovery. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-growth

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Growth & analytics (post-launch loop)** — the growth model and the events that measure it.

## Method
- Model **growth loops** alongside the funnel — trigger → action → output → reinvested input — and **name the primary loop** that compounds acquisition.
- Type **activation** as a bar: event + count + window (e.g. "created ≥3 projects within 7 days"), paired with a **time-to-value** target.
- Define the **retention curve / cohorts** and treat the **plateau** as the durable-growth check; for high-frequency products also pin a **stickiness ratio** (DAU/MAU or equivalent).
- Pin the **event-taxonomy naming convention** — object-action, controlled vocabulary — before listing events.

## Rules
- **post-launch and parallel** — don't gate the build on it; but its *analytics events* must reach the task breakdown so instrumentation is built in, not bolted on
- activation + retention are defined against the north-star; the experiment backlog has ≥1 `EXP-` carrying a metric
- **activation** is a typed bar (event + count + window) with a time-to-value target — never an adjective
- retention is a **cohort curve** whose plateau is the durable-growth check (+ a stickiness ratio when high-frequency)
- every experiment declares an **MDE**, **power/alpha**, derived **sample size**, **min-runtime**, a **guardrail metric**, and a **stop-rule** — no peeking unless a sequential method is declared
- events follow the pinned **object-action** controlled vocabulary and each carries an **owner**

## Output
**Stable IDs** (bare type prefix, ID = the leading table column / row key): `EXP-` a growth experiment.
Written under `commercial/growth/`:

| File | Captures | Format |
|---|---|---|
| `growth-model.md` | acquisition → activation → retention → referral/revenue (tied to north-star) + **named primary growth loop** (trigger→action→output→reinvested input) + activation bar (event·count·window) + time-to-value + retention-curve/cohorts (plateau · stickiness) + leading indicators | funnel · loop · fields |
| `experiments.md` | experiment backlog — id EXP-NNN | hypothesis · primary metric · MDE · power/alpha · sample size · min-runtime · guardrail metric · stop-rule |
| `analytics-events.md` | events/properties to track (object-action naming, with consent/tracking classification) + cohort/funnel definitions | event · properties · classification · owner |

ADRs → `adr/ADR-GRW-NNN.md`
Consumes: the compliance obligations / data classification (each event carries its consent/tracking class).

## Excludes
metric *targets* (→ the success metrics / goals) · the telemetry *plumbing* (→ the architecture) · pricing experiments' model (→ the commercial model)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
