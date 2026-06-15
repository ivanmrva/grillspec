# derive-observability — user guide

**Invoke:** `/derive-observability`  (plugin: `/grillspec:derive-observability`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Derive the observability design — SLOs/SLIs, telemetry, alerting, dashboards, runbooks — the basis for operating a real system. Use when the NFRs and architecture exist and you need operations designed.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-observability`
- **Standalone:** copy the `derive-observability/` folder into `~/.claude/skills/`, then run `/derive-observability`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
