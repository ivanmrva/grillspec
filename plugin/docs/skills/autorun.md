# autorun — user guide

**Invoke:** `/autorun`  (plugin: `/grillspec:autorun`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Unattended driver for the coding phase — works the build order one task at a time (or in parallel waves under pr delivery), drives each task to a green gate, lands it, and parks what needs a human.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:autorun` in Claude Code or `$grillspec:autorun` in Codex
- **Standalone:** copy the `autorun/` folder into `~/.claude/skills/` and run `/autorun` in Claude Code, or into `~/.agents/skills/` and run `$autorun` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
