# grill-growth — user guide

**Invoke:** `/grill-growth`  (plugin: `/grillspec:grill-growth`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Pin the post-launch growth model — activation/retention/referral, an experiment backlog, and the analytics events the product must emit to measure it. Use when you need a growth model plus its instrumentation; closes the loop from launch back to discovery.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-growth`
- **Standalone:** copy the `grill-growth/` folder into `~/.claude/skills/`, then run `/grill-growth`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
