# grill-monetization — user guide

**Invoke:** `/grill-monetization`  (plugin: `/grillspec:grill-monetization`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Pin the business model & pricing — model, packaging, plans/tiers, entitlements tied to real features, billing model, unit economics, and the customer-facing SLA/support commitments. Use when there are real features to price and you need the commercial model nailed down.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-monetization`
- **Standalone:** copy the `grill-monetization/` folder into `~/.claude/skills/`, then run `/grill-monetization`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
