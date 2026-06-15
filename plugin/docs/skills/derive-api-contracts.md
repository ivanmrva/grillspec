# derive-api-contracts — user guide

**Invoke:** `/derive-api-contracts`  (plugin: `/grillspec:derive-api-contracts`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Produce machine-readable API and event contracts — an `openapi.yaml` (latest-stable OpenAPI), an `asyncapi.yaml` (latest-stable AsyncAPI), schemas and versioning — from the published language and integration requirements. Use when the published language and integration requirements exist and you need the API/event contracts derived.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-api-contracts`
- **Standalone:** copy the `derive-api-contracts/` folder into `~/.claude/skills/`, then run `/derive-api-contracts`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
