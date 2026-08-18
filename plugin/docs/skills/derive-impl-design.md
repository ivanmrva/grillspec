# derive-impl-design — user guide

**Invoke:** `/derive-impl-design`  (plugin: `/grillspec:derive-impl-design`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Low-level design of the modules a hard slice touches — algorithm, error handling, concurrency — produced just-in-time before that slice is coded (design, not code; the architecture already fixed roles and seam interfaces).

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-impl-design` in Claude Code or `$grillspec:derive-impl-design` in Codex
- **Standalone:** copy the `derive-impl-design/` folder into `~/.claude/skills/` and run `/derive-impl-design` in Claude Code, or into `~/.agents/skills/` and run `$derive-impl-design` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
