# generate-ui-prototype — user guide

**Invoke:** `/generate-ui-prototype`  (plugin: `/grillspec:generate-ui-prototype`)

*Build / verify skill — it does work in your repo (no interview).*

## What it does
Generate a clickable HTML prototype of the screen(s) a UI slice implements — built from the real design-system tokens & components, with every interaction state, wired into the navigation the information architecture defines — as the precise visual + interaction reference the coding task builds against. Produced when a ux-heavy slice is finalized (the design-review window), not in the coding loop; skipped when the IA + design system already determine the screen.

## What it needs (input)
A task package and the code it touches.

## What it produces (output)
Writes its artifact.

## How to run it
- **In the bundle plugin:** `/grillspec:generate-ui-prototype`
- **Standalone:** copy the `generate-ui-prototype/` folder into `~/.claude/skills/`, then run `/generate-ui-prototype`. It works on its own and composes with sibling skills, each writing to its own output folder.

## How to tell it did its job  *(verification)*
Check the artifact covers its scope above, carries stable IDs, and records any gaps inline in the artifact (with a validation status for bets).
