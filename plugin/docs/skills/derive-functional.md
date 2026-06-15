# derive-functional — user guide

**Invoke:** `/derive-functional`  (plugin: `/grillspec:derive-functional`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Project the domain model into use-cases (commands × actors × flows) and testable acceptance criteria (invariants/rules/specs/policies). Use when the domain model exists and you need use-cases plus acceptance criteria projected from it.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-functional`
- **Standalone:** copy the `derive-functional/` folder into `~/.claude/skills/`, then run `/derive-functional`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
