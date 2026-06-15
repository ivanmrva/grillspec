# prototype — user guide

**Invoke:** `/prototype`  (plugin: `/grillspec:prototype`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Build a throwaway prototype to answer ONE open question empirically — a runnable terminal app for state/logic, or toggleable UI variations for design. Use when running code settles it better than discussing.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:prototype`
- **Standalone:** copy the `prototype/` folder into `~/.claude/skills/`, then run `/prototype`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
