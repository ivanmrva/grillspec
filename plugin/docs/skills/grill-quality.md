# grill-quality — user guide

**Invoke:** `/grill-quality`  (plugin: `/grillspec:grill-quality`)

*Interview skill — it asks you questions and writes a spec artifact.*

## What it does
Turn vague quality wishes into measurable targets (NFRs): a number, where it is measured and how it is enforced, with the architecture-shaping ones tagged as ASRs. Use when the design needs performance, reliability, security-level or accessibility bars it can be held to.

## What it needs (input)
A live, plain-language **interview** — it asks one question at a time; **no prior documents are required**. If you already have material, hand it over and it harvests from it before asking. It never refuses for lack of input.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:grill-quality` in Claude Code or `$grillspec:grill-quality` in Codex
- **Standalone:** copy the `grill-quality/` folder into `~/.claude/skills/` and run `/grill-quality` in Claude Code, or into `~/.agents/skills/` and run `$grill-quality` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).

> Sanity check while it runs: it should ask **one** question at a time, **recommend** a default on convergent forks (not quiz you on the obvious), and **never speak its internal jargon** at you.
