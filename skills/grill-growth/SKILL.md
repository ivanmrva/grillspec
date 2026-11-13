---
name: grill-growth
description: >-
  Pin the post-launch growth model: the activation bar, the retention definition, the growth
  loop, an experiment backlog, and the analytics events the product must emit to measure them. An
  optional commercial area; use only when the user asks for growth or analytics planning.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-growth

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Growth & analytics (post-launch loop)** — the growth model and the events that measure it.

Run this only when the user asks for it; nothing in the build path depends on it. When it is run, its analytics events are the one output the build picks up: the task that emits an event cites its `AEV-` id.

## Depth by profile
Optional at every profile. Capture what the user will use:

- By default, the activation bar, the retention definition and the analytics events needed to measure them.
- The growth-loop model, when the user is deciding where growth compounds.
- The experiment backlog, when the user is going to run experiments.

## Rules
- Activation and retention are defined against the north star. Activation is a typed bar (event + count + window, such as "created ≥ 3 projects within 7 days") with a time-to-value target. Where the goals already set the bar, refine it here.
- Retention is a cohort curve, and its plateau is the durable-growth check. A high-frequency product adds a stickiness ratio (DAU/MAU or an equivalent).
- Model growth loops beside the funnel (trigger → action → output → reinvested input) and name the primary loop, the one that compounds acquisition.
- Pin the event naming convention (object-action, from a controlled vocabulary) before listing events. Each event carries an owner and its consent or tracking classification.
- Each event has an `AEV-` id and names the `EXP-` or the metric it serves. An event no task cites is never instrumented, and the linter warns on it.
- Every experiment declares its hypothesis, primary metric, MDE, power and alpha, the sample size they imply, a minimum runtime, a guardrail metric and a stop rule. Read results at the planned horizon unless a sequential method is declared, because peeking inflates false positives.

## Output
**IDs:** `EXP-` a growth experiment · `AEV-` an analytics event.
Written under `commercial/growth/`:

| File | Captures | Format |
|---|---|---|
| `growth-model.md` | the funnel (acquisition → activation → retention → referral / revenue) tied to the north star · the activation bar and time-to-value · the retention curve and cohorts (plateau · stickiness) · the primary growth loop · leading indicators | funnel · typed fields · loop |
| `experiments.md` | the experiment backlog | `EXP-NNN` id · hypothesis · primary metric · MDE · power/alpha · sample size · min-runtime · guardrail metric · stop-rule |
| `analytics-events.md` | the events and properties to track, plus the cohort and funnel definitions | `AEV-NNN` id · event · properties · classification · serves(`EXP-` or metric) · owner |

ADRs → `adr/ADR-GRW-NNN.md`
Consumes: the goals (the north star and the activation bar), and the compliance obligations and data classification (each event's consent or tracking class).

## Excludes
metric *targets* (→ the success metrics / goals) · the telemetry *plumbing* (→ the architecture) · pricing experiments' model (→ the commercial model)

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
