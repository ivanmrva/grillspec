# generate-docs — user guide

**Invoke:** `/generate-docs`  (plugin: `/grillspec:generate-docs`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Generate the project's documentation — a self-contained static HTML doc-site that assembles the **full spec** (every area, discovery → delivery) plus the **implementation design** consolidated from the per-module/per-task designs — overview, domain, requirements, architecture, implementation, ADRs, traceability, glossary, dashboards. Re-runnable and CI-friendly.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:generate-docs`
- **Standalone:** copy the `generate-docs/` folder into `~/.claude/skills/`, then run `/generate-docs`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
