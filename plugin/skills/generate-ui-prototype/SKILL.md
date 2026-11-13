---
name: generate-ui-prototype
description: >-
  Build a clickable HTML prototype of a UI slice's screens from the real design-system tokens and components, every interaction state included — the visual reference the coding task builds against, reviewed by a human before the build. Loads the shared exec engine.
disable-model-invocation: true
argument-hint: the UI slice (its screen[s], from the UX requirements + design system)
---

# generate-ui-prototype

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill builds a clickable HTML prototype of the screens one UI slice implements. It is a kept reference, not a throwaway spike: the coding task builds against it, and the conformance review compares the built screen with it.

## When it runs
The prototype is made when the slice's task brief is being finalized, before the build. That is the attended moment when a human can look at the screen, ask for changes and approve it. Once approved, the brief's `prototype-review` row reads `frozen` and its `ux` row names the prototype's path, and a later build, possibly unattended, works against it without stopping to show anyone a screen.

Not every UI slice needs one. A prototype earns its place when the slice has composition of its own to pin down: a new screen or flow, states that are not obvious. A slice the information architecture and the design system already determine — a copy change, a field added to an existing form — has none, and its `ux` row reads `N/A — reuses DS-… on SCR-NNN`.

A slice with a real `ux` row is built unattended only after a human has seen its screen. The one exception is a brief that records `prototype-review: waived — <why>`: then the prototype is generated just before the build as the reference, and the owner has knowingly given up the review. Without the review or the waiver, the slice waits; an unreviewed screen is a visual decision nobody made.

## Process
1. **Take the slice's screens from the UX requirements**: the journey step, its place in the information architecture, and the interaction states it must have.
2. **Render each screen from the real design system** — its semantic and component tokens and the actual component variants and states — so the prototype and the code share one source for how things look. A component the design system lacks is a gap to raise there; inventing it in the prototype would freeze a design nobody specified.
3. **Include every interaction state the journey names** (empty, loading, success, error, permission-denied, as they apply), since the states are where a built screen most often falls short of its design.
4. **Wire the screen into the navigation the information architecture defines**, so it clicks through in context, and link it to its IDs: the `SCR-` it realises, its `JRN-` journey by ID, and the `UC-` and `DS-` elements it uses.
5. **Put it in front of the human**, apply what they ask for, and record the approval on the brief.

The prototype is rendered from the UX requirements and the design system, so a change belongs in those sources first and the screen is then rebuilt from them. An edit made only in the HTML would disagree with its sources and be lost at the next rebuild.

## Scope
- One slice's screens at a time. There is no global gallery to build: the overall structure is already the information architecture (navigation, layout, menus) and the design system.
- The app shell — navigation and layout — is itself a slice, usually the walking skeleton, and its screen is prototyped the same way.
- Self-contained HTML that opens without a build step (assets from a CDN are fine).
- Not production code, not the design-system definition, not the UX requirements, and not an exploratory spike (a throwaway that answers one question and is deleted).

## Output
Written under `prototypes/ui/` at the repo root, outside `spec/`:

| File | Captures | Format |
|---|---|---|
| `<screen>.html` | one screen, named after the `SCR-` it realises: real components and tokens · every interaction state · wired into the navigation · linked to its `SCR-`, `JRN-`, `UC-` and `DS-` IDs | self-contained HTML |
| `flows.md` | per journey, keyed by its `JRN-` ID: the `SCR-` → `SCR-` screen path and the `UC-` it serves. The conformance review walks this path on the built app, so keep it current as slices are added | table: journey · screen path · use-case |

The set of screens grows as UI slices are finalized.

Reads: the UX requirements (the slice's journey, its place in the information architecture, its states), the design system (tokens and components), and the slice's use-cases.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
