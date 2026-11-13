# deploy-release — user guide

**Invoke:** `/deploy-release`  (plugin: `/grillspec:deploy-release`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Promote a built increment along the project's promotion path — preflight, deploy through the pipeline, smoke-check, watch, roll back on breach — and prepare the production go/no-go for the human. Use when landed work needs to reach an environment.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:deploy-release` in Claude Code or `$grillspec:deploy-release` in Codex
- **Standalone:** copy the `deploy-release/` folder into `~/.claude/skills/` and run `/deploy-release` in Claude Code, or into `~/.agents/skills/` and run `$deploy-release` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
