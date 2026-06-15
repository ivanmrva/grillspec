# implement-task — user guide

**Invoke:** `/implement-task`  (plugin: `/grillspec:implement-task`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Implement one prepared task as a minimal, tested vertical slice — tests first, within architecture boundaries, code in the source tree (not the spec). Use when you have a prepared task to build.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:implement-task`
- **Standalone:** copy the `implement-task/` folder into `~/.claude/skills/`, then run `/implement-task`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
