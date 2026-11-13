# grill-integration-reqs — user guide

**Invoke:** `/grill-integration-reqs`  (plugin: `/grillspec:grill-integration-reqs`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Specify what each external seam must guarantee: direction, interaction style, volumes, SLA, delivery guarantee with idempotency, ordering and retry, failure behaviour and reconciliation. Use once the boundary interfaces are listed and a seam carries money, a delivery guarantee or a quota.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-integration-reqs` in Claude Code or `$grillspec:grill-integration-reqs` in Codex
- **Standalone:** copy the `grill-integration-reqs/` folder into `~/.claude/skills/` and run `/grill-integration-reqs` in Claude Code, or into `~/.agents/skills/` and run `$grill-integration-reqs` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
