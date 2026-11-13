# derive-test-strategy — user guide

**Invoke:** `/derive-test-strategy`  (plugin: `/grillspec:derive-test-strategy`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Decide the test strategy — the tier contract: what each tier covers, runs real, may mock, where it runs, and its coverage and mutation bars; at the regulated profile also traceability, edge discovery, NFR evidence and test data. Use when the spec and architecture exist.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-test-strategy` in Claude Code or `$grillspec:derive-test-strategy` in Codex
- **Standalone:** copy the `derive-test-strategy/` folder into `~/.claude/skills/` and run `/derive-test-strategy` in Claude Code, or into `~/.agents/skills/` and run `$derive-test-strategy` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
