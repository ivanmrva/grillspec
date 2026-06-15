# grill-integration-reqs — user guide

**Invoke:** `/grill-integration-reqs`  (plugin: `/grillspec:grill-integration-reqs`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Per external boundary, elicit the qualities and obligations of each exchange in detail — direction, interaction-style, volumes, latency, SLA, delivery guarantee + idempotency/ordering/retry/DLQ/replay, failure/degradation behaviour, reconciliation, auth. Use when the boundary roster already exists and you need each seam specified.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-integration-reqs`
- **Standalone:** copy the `grill-integration-reqs/` folder into `~/.claude/skills/`, then run `/grill-integration-reqs`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
