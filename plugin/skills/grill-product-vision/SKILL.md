---
name: grill-product-vision
description: >-
  Define the product in plain language — what it is and the outcome, the value proposition, a one-line positioning statement with differentiation, a coarse in/out scope with explicit non-goals, coarse MVP/near/deferred phasing, and the go-to-market **motion** (PLG / self-serve vs sales-led) — the early fork that shapes onboarding, billing and auth. The scope here seeds which contexts the domain model covers. Use when you need vision, positioning, a revisable scope, and the motion set before architecture. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-product-vision

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Product vision** — what the product is, who it wins for, and a coarse scope.

## Rules
- scope is **coarse & revisable** — don't demand precision; it sharpens once the functional spec reveals reality
- in/out scope needs **explicit non-goals** (what we deliberately won't do), not just an in-list
- positioning is built **bottom-up** — capture competitive-alternatives → unique-attributes → differentiated-value → best-fit-segment → market-category as fields, then let them *feed* the one-liner; the **category is an output, not an input** (it falls out of the alternatives + value, never assumed up front)
- positioning collapses to **one line**: for <target> who <need>, <product> is a <category> that <benefit>; unlike <alt>, we <differentiator>
- the **value-prop line must trace to the top-ranked job/pain/gain** — name which one it relieves, or it's a slogan
- the **go-to-market motion** (PLG / self-serve vs sales-led vs hybrid) is decided here — an early product-strategy fork that shapes onboarding, in-app billing, and auth/SSO, so it can't wait for go-to-market execution

## Output
Written under `product/vision/`:

| File | Captures | Format |
|---|---|---|
| `vision.md` | vision + value proposition (the prop line traces to the top-ranked job/pain/gain) | vision: 1–2 lines · value prop: 1 line + the job/pain/gain it relieves |
| `positioning.md` | the bottom-up fields that feed the one-liner, then the statement | competitive-alternatives → unique-attributes → differentiated-value → best-fit-segment → market-category (derived) → one-line statement |
| `scope.md` | coarse scope — named capability areas in/out (seed candidate domain contexts) + phasing | in / out lists · MVP / near / deferred |
| `motion.md` | the go-to-market motion / sales model: PLG · self-serve · sales-led · hybrid — the early fork that drives onboarding, in-app billing & auth/SSO | motion · rationale |

ADRs → `adr/ADR-VIS-NNN.md`
Consumes: the **validated problem** — the problem hypothesis + DVF bets the vision answers (from discovery).

## Excludes
detailed features · pricing · metrics · delivery dates & scheduling

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
