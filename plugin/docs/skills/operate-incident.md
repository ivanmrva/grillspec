# operate-incident — user guide

**Invoke:** `/operate-incident`  (plugin: `/grillspec:operate-incident`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Work a production incident — triage, restore service by the runbook, keep the timeline, find the root cause, and turn what was learned into a fix and a spec change. Use during or just after an incident.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:operate-incident` in Claude Code or `$grillspec:operate-incident` in Codex
- **Standalone:** copy the `operate-incident/` folder into `~/.claude/skills/` and run `/operate-incident` in Claude Code, or into `~/.agents/skills/` and run `$operate-incident` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
