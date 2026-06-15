# grill-customer-discovery — user guide

**Invoke:** `/grill-customer-discovery`  (plugin: `/grillspec:grill-customer-discovery`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Pin who the product is for — target market & segments, personas with the B2B decision-making unit, and the jobs-to-be-done behind each. Flags which personas are system users, seeding the shared actor roster. Use when you need the primary segment, its JTBD, and the personas nailed.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-customer-discovery`
- **Standalone:** copy the `grill-customer-discovery/` folder into `~/.claude/skills/`, then run `/grill-customer-discovery`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
