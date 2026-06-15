# run-tests — user guide

**Invoke:** `/run-tests`  (plugin: `/grillspec:run-tests`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Run a task's suite and gate on it — suite green, every acceptance criterion exercised at the right level, coverage met. Use when a task's code is written and you need to verify it.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:run-tests`
- **Standalone:** copy the `run-tests/` folder into `~/.claude/skills/`, then run `/run-tests`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
