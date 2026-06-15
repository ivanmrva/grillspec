# derive-impl-design — user guide

**Invoke:** `/derive-impl-design`  (plugin: `/grillspec:derive-impl-design`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Low-level design of the modules a slice touches — algorithm, error handling, concurrency — produced just-in-time for a complex slice, just before it is coded (DESIGN, not code). The architecture already fixed each module's role, dependency direction, and seam interface; this designs the internals behind it. Use for a hard slice (tricky algorithm · real concurrency · cross-context saga) before implementing it.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-impl-design`
- **Standalone:** copy the `derive-impl-design/` folder into `~/.claude/skills/`, then run `/derive-impl-design`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
