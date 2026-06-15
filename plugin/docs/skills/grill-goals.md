# grill-goals — user guide

**Invoke:** `/grill-goals`  (plugin: `/grillspec:grill-goals`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Define what success means — a north-star metric with its input-metric tree, supporting success metrics, guardrail/counter-metrics, and pre-committed KILL-CRITERIA ('if not X by Y, we stop'). Use when you need success and the stop conditions pinned.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-goals`
- **Standalone:** copy the `grill-goals/` folder into `~/.claude/skills/`, then run `/grill-goals`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
