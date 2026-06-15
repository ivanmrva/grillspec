# derive-infra-ops — user guide

**Invoke:** `/derive-infra-ops`  (plugin: `/grillspec:derive-infra-ops`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Design topology, IaC, CI/CD, deploy/release strategy, environments, scaling/HA, DR/BCP, backup/restore, capacity and cost from the NFRs and constraints. Use when the NFRs and constraints exist and you need the deploy & operations architecture designed.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-infra-ops`
- **Standalone:** copy the `derive-infra-ops/` folder into `~/.claude/skills/`, then run `/derive-infra-ops`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
