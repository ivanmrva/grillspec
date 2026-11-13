# diagnose — user guide

**Invoke:** `/diagnose`  (plugin: `/grillspec:diagnose`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Diagnose a hard bug or performance regression with a disciplined loop — a fast deterministic pass/fail signal, ranked falsifiable hypotheses, one variable at a time, a fix with a regression test. Use when a quick patch has not found the cause.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:diagnose` in Claude Code or `$grillspec:diagnose` in Codex
- **Standalone:** copy the `diagnose/` folder into `~/.claude/skills/` and run `/diagnose` in Claude Code, or into `~/.agents/skills/` and run `$diagnose` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
