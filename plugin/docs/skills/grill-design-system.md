# grill-design-system — user guide

**Invoke:** `/grill-design-system`  (plugin: `/grillspec:grill-design-system`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Pin the design system as a spec — design tokens (DTCG, primitive→semantic→component), components-as-contracts (variants · states · ARIA), implementation mapping, accessibility baked into the tokens, brand & assets, and voice/content. Provided, partial, or generated from a brand seed. Use when you need the design system specified, not the journeys.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-design-system`
- **Standalone:** copy the `grill-design-system/` folder into `~/.claude/skills/`, then run `/grill-design-system`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
