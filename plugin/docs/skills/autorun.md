# autorun — user guide

**Invoke:** `/autorun`  (plugin: `/grillspec:autorun`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Autonomous AFK driver for the coding phase — drives the per-task implement → done-gate → conformance loop across the task DAG in parallel, self-correcting code to green, merging on green, unlocking dependents, parking true HITL needs. Use when the spec is implementation-final and you want the coding phase driven AFK across the whole DAG.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:autorun`
- **Standalone:** copy the `autorun/` folder into `~/.claude/skills/`, then run `/autorun`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
