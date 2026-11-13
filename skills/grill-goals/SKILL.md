---
name: grill-goals
description: >-
  Define what success means: a north-star metric with the levers that move it, supporting metrics
  and guardrails, and pre-committed kill-criteria ("if not X by Y, we stop"). Use when the product
  needs measurable goals and a stop rule.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-goals

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Goals, metrics & kill-criteria** — the single metric that signals it's working and the conditions under which we stop.

## Depth by profile
| Profile | What the interview captures |
|---|---|
| `lite` | not a separate area: the product vision carries the one success metric and the kill-criterion. |
| `standard`, `regulated` | the three files below, kept tight: the north star with 3–5 levers, only the supporting metrics and guardrails someone will review, and the kill-criteria. |

## Rules
- The north star comes with its input-metric tree: the 3–5 levers that causally move it, spread over the funnel (acquisition → activation → retention → referral → revenue).
- Every metric has an operational definition (numerator / denominator / window), because an adjective cannot be measured.
- The activation bar (event + count + window) is set here and ratified by the user. It is a pre-committed definition of success that the growth area only refines, and that area may never run.
- Name the guardrail metrics: what must not degrade while the north star is optimised.
- Kill-criteria are stop conditions committed before the evidence arrives. Frame each as a pivot / persevere / kill decision on a fixed review cadence, and add a minimum-success criterion: what success must at least look like, by when.
- Every target, threshold and deadline is the user's to ratify.

## Output
Written under `product/goals/`:

| File | Captures | Format |
|---|---|---|
| `north-star.md` | the north-star metric and its input-metric tree | metric + why (1 line) · 3–5 causal levers across the funnel, with activation and retention operationally defined |
| `success-metrics.md` | supporting metrics and guardrails | metric · operational definition (num / denom / window) · target |
| `kill-criteria.md` | the pre-committed decisions, the review cadence and the minimum-success bar | table: `signal · threshold · deadline · verdict (pivot/persevere/kill) · status (unconfirmed/ratified)` + review-cadence and minimum-success rows |

State a deadline relative to a milestone ("week 12 after launch") so the file reads as a rule.

ADRs → `adr/ADR-GOAL-NNN.md`
Consumes: the product vision — the outcome these metrics and kill-criteria measure.

## Excludes
unit economics · analytics implementation & dashboards

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
