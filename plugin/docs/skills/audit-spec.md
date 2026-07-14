# audit-spec — user guide

**Invoke:** `/audit-spec`  (plugin: `/grillspec:audit-spec`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Audit an EXISTING spec for completeness, internal consistency, contradictions, branch coverage (product · domain · software), and whether a coding agent can build it WITHOUT guessing. Two depths: `consistency` (the judgment the linter can't make — semantic contradictions, scope adherence, decision coherence) and `full` (adds the domain/usage completeness pass that finds what's MISSING). Only `full` can declare code-gen readiness. The judgment layer ABOVE the mechanical tools, distinct from the per-task code-vs-spec conformance review. Report-only by default; `--fix` remediates the findings in-session (routed fixes + full propagation through every derived layer, 10-delivery included); `--loop` repeats fix-passes with a parallel read-only auditor fan-out until the spec converges to ZERO findings (K consecutive dry batches). Use --loop when asked to "drive the spec to zero audit findings", "loop the audit until clean", or "exhaustively remediate the spec".

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:audit-spec` in Claude Code or `$grillspec:audit-spec` in Codex
- **Standalone:** copy the `audit-spec/` folder into `~/.claude/skills/` and run `/audit-spec` in Claude Code, or into `~/.agents/skills/` and run `$audit-spec` in Codex. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
