# deploy-release — user guide

**Invoke:** `/deploy-release`  (plugin: `/grillspec:deploy-release`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Promote a built increment through environments with an explicit rollout/rollback strategy and smoke-verify in the target. Use when a merged increment needs promoting to an environment.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:deploy-release`
- **Standalone:** copy the `deploy-release/` folder into `~/.claude/skills/`, then run `/deploy-release`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
