# grill-problem-validation — user guide

**Invoke:** `/grill-problem-validation`  (plugin: `/grillspec:grill-problem-validation`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Pin the problem worth solving and score the riskiest bets — problem hypothesis (who hurts, how badly, vs which alternatives, why-now), desirability/viability/feasibility bets scored criticality × uncertainty, value-proposition fit, and a PMF definition with the cheapest test per assumption. Runs first and never closes. Use when you need the problem nailed and the riskiest bets scored before anything is built.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-problem-validation`
- **Standalone:** copy the `grill-problem-validation/` folder into `~/.claude/skills/`, then run `/grill-problem-validation`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
