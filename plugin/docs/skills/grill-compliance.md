# grill-compliance — user guide

**Invoke:** `/grill-compliance`  (plugin: `/grillspec:grill-compliance`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Pin which regulatory/legal regimes apply and turn them into concrete, referenceable obligations (`OBL-`) that flow into security, data, and architecture. Swiss/EU-aware (FADP/GDPR/EU AI Act). Use when you need the applicable regimes and their obligations nailed down.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-compliance`
- **Standalone:** copy the `grill-compliance/` folder into `~/.claude/skills/`, then run `/grill-compliance`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
