# grill-product-vision — user guide

**Invoke:** `/grill-product-vision`  (plugin: `/grillspec:grill-product-vision`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Define the product in plain language — what it is and the outcome, the value proposition, a one-line positioning statement with differentiation, a coarse in/out scope with explicit non-goals, coarse MVP/near/deferred phasing, and the go-to-market **motion** (PLG / self-serve vs sales-led) — the early fork that shapes onboarding, billing and auth. The scope here seeds which contexts the domain model covers. Use when you need vision, positioning, a revisable scope, and the motion set before architecture.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-product-vision`
- **Standalone:** copy the `grill-product-vision/` folder into `~/.claude/skills/`, then run `/grill-product-vision`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
