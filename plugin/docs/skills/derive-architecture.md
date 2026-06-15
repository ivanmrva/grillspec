# derive-architecture — user guide

**Invoke:** `/derive-architecture`  (plugin: `/grillspec:derive-architecture`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Derive the solution architecture — style, C4 decomposition, tech stack, contexts→services, cross-cutting concerns, the module map & seam contracts, and the key sequences — from the settled spec. Use when the requirements are settled and you need the architecture derived (not interviewed).

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-architecture`
- **Standalone:** copy the `derive-architecture/` folder into `~/.claude/skills/`, then run `/derive-architecture`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
