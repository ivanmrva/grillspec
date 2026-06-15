# generate-api-reference — user guide

**Invoke:** `/generate-api-reference`  (plugin: `/grillspec:generate-api-reference`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Generate API reference docs from the API-/EVT- contracts — endpoints, schemas, auth, errors, examples — as static HTML. Embedded in the doc-site or standalone.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:generate-api-reference`
- **Standalone:** copy the `generate-api-reference/` folder into `~/.claude/skills/`, then run `/generate-api-reference`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
