# derive-conventions — user guide

**Invoke:** `/derive-conventions`  (plugin: `/grillspec:derive-conventions`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Derive the coding agent's standards and runway from the architecture — style, boundary rules as fitness checks, workflow, build/run/test/lint commands, Definition of Done — generating canonical root AGENTS.md plus an import-only CLAUDE.md adapter.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-conventions` in Claude Code or `$grillspec:derive-conventions` in Codex
- **Standalone:** copy the `derive-conventions/` folder into `~/.claude/skills/` and run `/derive-conventions` in Claude Code, or into `~/.agents/skills/` and run `$derive-conventions` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
