# grill-go-to-market — user guide

**Invoke:** `/grill-go-to-market`  (plugin: `/grillspec:grill-go-to-market`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Pin the go-to-market execution — ICP, channels & per-channel messaging, launch plan, partnerships — aligned to the product's chosen go-to-market motion. Use when you need a GTM plan; late/parallel and optional, not part of the core system spec.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-go-to-market`
- **Standalone:** copy the `grill-go-to-market/` folder into `~/.claude/skills/`, then run `/grill-go-to-market`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
