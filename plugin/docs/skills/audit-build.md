# audit-build — user guide

**Invoke:** `/audit-build`  (plugin: `/grillspec:audit-build`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
The whole-build audit — the independent, release-time attestation that the BUILD followed the spec's declared process: the evidence ledger really ran, cross-task emergent properties hold, the operate ledger reconciles. Distrusts per-task self-reports by design; report-only, no fix mode — fixes route to the task machinery, then a fresh re-audit.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:audit-build` in Claude Code or `$grillspec:audit-build` in Codex
- **Standalone:** copy the `audit-build/` folder into `~/.claude/skills/` and run `/audit-build` in Claude Code, or into `~/.agents/skills/` and run `$audit-build` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
