# grill-ddd — user guide

**Invoke:** `/grill-ddd`  (plugin: `/grillspec:grill-ddd`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Turn an idea or existing docs into a complete Domain-Driven Design model — subdomains, bounded contexts, aggregates — building the ubiquitous language and actor roster as it goes. Use when modelling a domain, even if the user never says "DDD".

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-ddd`
- **Standalone:** copy the `grill-ddd/` folder into `~/.claude/skills/`, then run `/grill-ddd`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
