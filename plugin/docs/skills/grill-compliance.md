# grill-compliance — user guide

**Invoke:** `/grill-compliance`  (plugin: `/grillspec:grill-compliance`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Pin which regulatory and legal regimes apply and turn them into concrete, referenceable obligations (OBL-), each with the control that owns it. Swiss/EU-aware (FADP, GDPR, EU AI Act). Use when the product handles personal data, embeds AI, or sells into a regulated market.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-compliance` in Claude Code or `$grillspec:grill-compliance` in Codex
- **Standalone:** copy the `grill-compliance/` folder into `~/.claude/skills/` and run `/grill-compliance` in Claude Code, or into `~/.agents/skills/` and run `$grill-compliance` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
