# grill-product-vision — user guide

**Invoke:** `/grill-product-vision`  (plugin: `/grillspec:grill-product-vision`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Define the product in plain language: the value proposition, a coarse scope with explicit non-goals, MVP/near/deferred phasing, and the go-to-market motion (self-serve or sales-led) that shapes onboarding, billing and auth. Use when starting a product or re-cutting its scope.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-product-vision` in Claude Code or `$grillspec:grill-product-vision` in Codex
- **Standalone:** copy the `grill-product-vision/` folder into `~/.claude/skills/` and run `/grill-product-vision` in Claude Code, or into `~/.agents/skills/` and run `$grill-product-vision` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
