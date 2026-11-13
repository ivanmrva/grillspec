---
name: grill-product-vision
description: >-
  Define the product in plain language: the value proposition, a coarse scope with explicit
  non-goals, MVP/near/deferred phasing, and the go-to-market motion (self-serve or sales-led) that
  shapes onboarding, billing and auth. Use when starting a product or re-cutting its scope.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-product-vision

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Product vision** — what the product is, who it wins for, and a coarse scope.

## Depth by profile
| Profile | What the interview captures |
|---|---|
| every profile | `vision.md`, `scope.md` and `motion.md`: the value proposition, the capability areas in and out of scope with the non-goals, the phasing, and the motion. |
| `lite` | `vision.md` also carries what larger profiles keep in separate areas. One paragraph says who the product is for: the primary user and the job they hire it for. The goal is one success metric with its target, plus the kill-criterion (signal · threshold · deadline). Both goal values are the user's to ratify. |
| `standard`, `regulated` | goals and kill-criteria belong to the goals area. Keep the who-it-is-for paragraph unless a customer-discovery area exists. |
| on request | `positioning.md`, when the user wants positioning worked out. It feeds go-to-market messaging and nothing in the build. |

## Rules
- Scope is coarse and revisable. Name capability areas, not features; the functional spec sharpens them later, so precision here is wasted effort.
- Scope states what is out as well as what is in. Explicit non-goals (what the product deliberately will not do) stop later areas from re-opening the question.
- The value-proposition line names the top-ranked job, pain or gain it relieves. Without that link it is a slogan.
- The go-to-market motion (PLG / self-serve · sales-led · hybrid) is decided here because it shapes onboarding, in-app billing and auth/SSO, which the build needs long before go-to-market planning starts.
- Positioning, when written, is built bottom-up: competitive alternatives → unique attributes → differentiated value → best-fit segment → market category. The category falls out of the alternatives and the value; it is an output of the chain. The fields feed one line: "for <target> who <need>, <product> is a <category> that <benefit>; unlike <alt>, we <differentiator>".

## Output
Written under `product/vision/`:

| File | Captures | Format |
|---|---|---|
| `vision.md` | the vision and the value proposition; at `lite` also who it is for, the success metric and the kill-criterion | vision: 1–2 lines · value prop: 1 line + the job/pain/gain it relieves |
| `scope.md` | coarse scope: named capability areas (`CA-`) in and out, which seed the candidate domain contexts, plus phasing | in / out lists keyed on `CA-` · MVP / near / deferred |
| `motion.md` | the go-to-market motion: PLG · self-serve · sales-led · hybrid | motion · rationale |
| `positioning.md` | the bottom-up fields, then the one-line statement | competitive alternatives → unique attributes → differentiated value → best-fit segment → market category → statement |

ADRs → `adr/ADR-VIS-NNN.md`
Consumes: the validated problem — the problem hypothesis and the bets the vision answers (from discovery).

## Excludes
detailed features · pricing · the metric tree and guardrails (→ goals) · delivery dates & scheduling

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
