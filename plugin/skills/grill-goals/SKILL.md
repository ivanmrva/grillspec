---
name: grill-goals
description: >-
  Define what success means — a north-star metric with its input-metric tree, supporting success metrics, guardrail/counter-metrics, and pre-committed KILL-CRITERIA ('if not X by Y, we stop'). Use when you need success and the stop conditions pinned. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-goals

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Goals, metrics & kill-criteria** — the single metric that signals it's working and the conditions under which we stop.

## Rules
- the north-star comes with its **input-metric tree** — the 3–5 levers that *causally* move it, spanning the full funnel: **acquisition → activation → retention → referral → revenue**, with **activation and retention operationally defined** (not left as adjectives)
- every metric has an **operational definition** (numerator / denominator / window) — never an adjective
- name **guardrail/counter-metrics**: what must not degrade while optimising the north-star
- **kill-criteria are pre-committed** stop conditions, set now — not authored after the fact
- frame each as a **pivot / persevere / kill decision** on a **fixed review cadence**, laddering up to a **minimum-success criterion** — what success must at least look like by when — not just an isolated "stop if X"

## Output
Written under `product/goals/`:

| File | Captures | Format |
|---|---|---|
| `north-star.md` | the north-star metric + its input-metric tree across the funnel | metric + why (1 line) · 3–5 causal levers spanning acquisition→activation→retention→referral→revenue (activation & retention operationally defined) |
| `success-metrics.md` | supporting metrics + guardrails | metric · operational definition (num/denom/window) · target |
| `kill-criteria.md` | pre-committed pivot/persevere/kill decision on a fixed cadence, laddering to a minimum-success bar | review cadence · per signal: 'if <metric> not <threshold> by <date>' → pivot/persevere/kill · minimum-success criterion |

ADRs → `adr/ADR-GOAL-NNN.md`

## Excludes
unit economics · analytics implementation & dashboards

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
