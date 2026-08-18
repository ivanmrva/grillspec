# audit-spec — user guide

**Invoke:** `/audit-spec`  (plugin: `/grillspec:audit-spec`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Audit an EXISTING spec for completeness, consistency, contradictions, and whether a coding agent can build it without guessing — the judgment layer above the mechanical tools. Report-only by default; --fix remediates in-session, --loop converges to zero findings. Only --depth full declares code-gen readiness.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:audit-spec` in Claude Code or `$grillspec:audit-spec` in Codex
- **Standalone:** copy the `audit-spec/` folder into `~/.claude/skills/` and run `/audit-spec` in Claude Code, or into `~/.agents/skills/` and run `$audit-spec` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
