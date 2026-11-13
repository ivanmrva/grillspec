# generate-api-reference — user guide

**Invoke:** `/generate-api-reference`  (plugin: `/grillspec:generate-api-reference`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Publish API reference docs as static HTML from the API and event contracts — endpoints, schemas, auth, errors, examples, deprecations. Use when the API reference should be built or refreshed, on its own or inside the docs site.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:generate-api-reference` in Claude Code or `$grillspec:generate-api-reference` in Codex
- **Standalone:** copy the `generate-api-reference/` folder into `~/.claude/skills/` and run `/generate-api-reference` in Claude Code, or into `~/.agents/skills/` and run `$generate-api-reference` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
