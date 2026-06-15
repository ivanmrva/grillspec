# grill-market — user guide

**Invoke:** `/grill-market`  (plugin: `/grillspec:grill-market`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Map the competitive landscape — direct competitors in a comparison matrix, indirect alternatives incl. status-quo/DIY, defensible differentiation with named moats, switching costs, and order-of-magnitude sizing. Feeds positioning and the viability bet. Use when you need the landscape and rough size mapped, not a financial model.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-market`
- **Standalone:** copy the `grill-market/` folder into `~/.claude/skills/`, then run `/grill-market`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
