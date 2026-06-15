# derive-security-architecture — user guide

**Invoke:** `/derive-security-architecture`  (plugin: `/grillspec:derive-security-architecture`)

*Derivation skill — it generates an artifact from recorded input (no interview).*

## What it does
Design authn/authz mechanisms, encryption, secrets and identity from the security requirements. Use when the security requirements exist and you need authn/authz, encryption and secrets mechanisms designed.

## What it needs (input)
The **recorded source artifacts** — it derives from them and does **not** interview you for facts. Standalone, place those artifacts in the working-root folders (or hand them in); a missing fact is recorded as a gap, never invented.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:derive-security-architecture`
- **Standalone:** copy the `derive-security-architecture/` folder into `~/.claude/skills/`, then run `/derive-security-architecture`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
