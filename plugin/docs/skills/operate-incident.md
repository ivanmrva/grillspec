# operate-incident — user guide

**Invoke:** `/operate-incident`  (plugin: `/grillspec:operate-incident`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Triage a production incident via runbooks, mitigate, and capture every learning as a new assumption or gap that propagates upstream. Use during or just after an incident.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:operate-incident`
- **Standalone:** copy the `operate-incident/` folder into `~/.claude/skills/`, then run `/operate-incident`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
