# grill-system-context — user guide

**Invoke:** `/grill-system-context`  (plugin: `/grillspec:grill-system-context`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Nail the system boundary before the domain is modelled — the system as one black box, its external actors and neighbor systems, the interfaces that cross the edge, and the in/out scope line, drawn as the C4 System Context view.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-system-context`
- **Standalone:** copy the `grill-system-context/` folder into `~/.claude/skills/`, then run `/grill-system-context`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
