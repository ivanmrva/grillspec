# conformance-review — user guide

**Invoke:** `/conformance-review`  (plugin: `/grillspec:conformance-review`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
The post-task review of generated code against OUR spec — run after each task, before the next. Lens A: conformance vs spec/architecture/contracts/security/NFR-evidence/traceability (blocking); Lens B: design health (advisory). Its VERDICT becomes the task's conformance gate row.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:conformance-review` in Claude Code or `$grillspec:conformance-review` in Codex
- **Standalone:** copy the `conformance-review/` folder into `~/.claude/skills/` and run `/conformance-review` in Claude Code, or into `~/.agents/skills/` and run `$conformance-review` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
