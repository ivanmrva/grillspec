# audit-spec — user guide

**Invoke:** `/audit-spec`  (plugin: `/grillspec:audit-spec`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
The whole-spec audit — verify an EXISTING spec is complete, internally consistent, contradiction-free, covers all branches (product · domain · software), and is good enough that a coding agent can build from it WITHOUT guessing. Two depths: `consistency` (the judgment the linter can't make — semantic contradictions, scope adherence, decision coherence) and `full` (adds the domain/usage completeness pass that finds what's MISSING). Only `full` can declare code-gen readiness. The judgment layer ABOVE the mechanical tools, distinct from the per-task conformance-review.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:audit-spec`
- **Standalone:** copy the `audit-spec/` folder into `~/.claude/skills/`, then run `/audit-spec`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
