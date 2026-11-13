# audit-spec — user guide

**Invoke:** `/audit-spec`  (plugin: `/grillspec:audit-spec`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Audit an existing spec for consistency, completeness against its project profile, leanness, and whether an agent can build from it without guessing — the judgment above the linter. Report-only by default; --fix remediates, --loop repeats until a pass finds nothing.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:audit-spec` in Claude Code or `$grillspec:audit-spec` in Codex
- **Standalone:** copy the `audit-spec/` folder into `~/.claude/skills/` and run `/audit-spec` in Claude Code, or into `~/.agents/skills/` and run `$audit-spec` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
