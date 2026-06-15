# grill-data-reqs — user guide

**Invoke:** `/grill-data-reqs`  (plugin: `/grillspec:grill-data-reqs`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Elicit the non-structural data requirements the logical model doesn't carry — classification, ownership, retention, residency, volume, integrity. Use when you need data governance, not storage design.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-data-reqs`
- **Standalone:** copy the `grill-data-reqs/` folder into `~/.claude/skills/`, then run `/grill-data-reqs`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
