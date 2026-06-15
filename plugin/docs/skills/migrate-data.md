# migrate-data — user guide

**Invoke:** `/migrate-data`  (plugin: `/grillspec:migrate-data`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Generate and run the schema/data migration a DATA-/AGG- change requires — forward + rollback, idempotent, online-safe, verified. Mandatory whenever the data model changes.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:migrate-data`
- **Standalone:** copy the `migrate-data/` folder into `~/.claude/skills/`, then run `/migrate-data`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
