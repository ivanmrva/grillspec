# derive-tasks — user guide

**Invoke:** `/derive-tasks`  (plugin: `/grillspec:derive-tasks`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Break a spec into small, vertically sliced task briefs a coding agent can build from — each self-contained, risk-tiered, phase-tagged and dependency-ordered, walking skeleton first. Use when the spec needs turning into build-ready work.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-tasks` in Claude Code or `$grillspec:derive-tasks` in Codex
- **Standalone:** copy the `derive-tasks/` folder into `~/.claude/skills/` and run `/derive-tasks` in Claude Code, or into `~/.agents/skills/` and run `$derive-tasks` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
