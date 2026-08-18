# generate-docs — user guide

**Invoke:** `/generate-docs`  (plugin: `/grillspec:generate-docs`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Generate the project's documentation — a self-contained static HTML doc-site assembling the full spec plus the consolidated implementation design: overview, domain, requirements, architecture, ADRs, traceability, glossary, dashboards. Re-runnable and CI-friendly.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:generate-docs` in Claude Code or `$grillspec:generate-docs` in Codex
- **Standalone:** copy the `generate-docs/` folder into `~/.claude/skills/` and run `/generate-docs` in Claude Code, or into `~/.agents/skills/` and run `$generate-docs` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
