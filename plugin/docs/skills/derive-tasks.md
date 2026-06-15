# derive-tasks — user guide

**Invoke:** `/derive-tasks`  (plugin: `/grillspec:derive-tasks`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Break a spec into minimal, vertically-sliced, build-ready tasks for a coding agent — each a complete reference manifest, phase-tagged and dependency-ordered, walking-skeleton first. Use when you need the spec turned into build-ready slices.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-tasks`
- **Standalone:** copy the `derive-tasks/` folder into `~/.claude/skills/`, then run `/derive-tasks`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
