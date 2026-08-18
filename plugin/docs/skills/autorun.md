# autorun — user guide

**Invoke:** `/autorun`  (plugin: `/grillspec:autorun`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Autonomous AFK driver for the coding phase — runs the per-task implement → done-gate → conformance loop across the task DAG in parallel, self-correcting to green, merging on green, parking true HITL blockers.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:autorun` in Claude Code or `$grillspec:autorun` in Codex
- **Standalone:** copy the `autorun/` folder into `~/.claude/skills/` and run `/autorun` in Claude Code, or into `~/.agents/skills/` and run `$autorun` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
