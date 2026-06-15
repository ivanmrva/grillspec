# derive-test-strategy — user guide

**Invoke:** `/derive-test-strategy`  (plugin: `/grillspec:derive-test-strategy`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Derive the two-tier test architecture — levels, coverage, traceability — and make testing an active edge-case discovery engine, not just verification. Use when the spec exists and you need the test strategy defined.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-test-strategy`
- **Standalone:** copy the `derive-test-strategy/` folder into `~/.claude/skills/`, then run `/derive-test-strategy`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
