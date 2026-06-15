# diagnose — user guide

**Invoke:** `/diagnose`  (plugin: `/grillspec:diagnose`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Disciplined diagnosis loop for hard bugs and performance regressions — build a fast deterministic feedback loop, reproduce, rank falsifiable hypotheses, instrument one variable at a time, fix with a regression test, post-mortem. Use when a hard bug or regression needs root-causing, not a quick patch.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:diagnose`
- **Standalone:** copy the `diagnose/` folder into `~/.claude/skills/`, then run `/diagnose`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
