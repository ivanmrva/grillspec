# migrate-data — user guide

**Invoke:** `/migrate-data`  (plugin: `/grillspec:migrate-data`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Write and run a schema or data migration that touches existing data — forward and rollback, idempotent, online-safe, verified before production. Use for a backfill, a transform, a large-table change, a store move or a production load.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:migrate-data` in Claude Code or `$grillspec:migrate-data` in Codex
- **Standalone:** copy the `migrate-data/` folder into `~/.claude/skills/` and run `/migrate-data` in Claude Code, or into `~/.agents/skills/` and run `$migrate-data` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
