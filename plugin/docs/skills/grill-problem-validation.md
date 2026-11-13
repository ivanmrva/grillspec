# grill-problem-validation — user guide

**Invoke:** `/grill-problem-validation`  (plugin: `/grillspec:grill-problem-validation`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Pin the problem worth solving and the risky bets behind it: the problem hypothesis, then each desirability, viability and feasibility bet with its criticality, status and cheapest test. Use at the start of a product and whenever new evidence changes a bet.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-problem-validation` in Claude Code or `$grillspec:grill-problem-validation` in Codex
- **Standalone:** copy the `grill-problem-validation/` folder into `~/.claude/skills/` and run `/grill-problem-validation` in Claude Code, or into `~/.agents/skills/` and run `$grill-problem-validation` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
