---
name: generate-ui-prototype
description: >-
  Generate a clickable HTML prototype of the screen(s) a UI slice implements — built from the real design-system tokens & components, with every interaction state, wired into the navigation the information architecture defines — as the precise visual + interaction reference the coding task builds against. Per-slice, just-in-time. Loads the shared exec core.
disable-model-invocation: true
argument-hint: the UI slice (its screen[s], from the UX requirements + design system)
---

# generate-ui-prototype

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **a clickable HTML prototype of the screen(s) a UI slice implements** — generated just-in-time for that slice, as the exact reference the coding task builds against (kept + versioned, not a throwaway spike).

## Process
1. **Take the slice's screen(s)** from the UX requirements — the journey step, its place in the information architecture, and its required interaction states.
2. **Render each screen** from the **real design-system tokens & components** (semantic/component tokens, the actual component variants/states — never ad-hoc styling), covering every interaction state (empty · loading · success · error · permission-denied).
3. **Wire it into the navigation** the IA defines (so it clicks through in context); cross-link the screen to its `UC-`/`DS-` IDs.
4. **Regenerate** the slice's screen on a UX/design-system change — it's a projection, not hand-maintained.

## Rules
- **per-slice, JIT** — generated for the screen(s) of the slice being built, not as a global pre-built gallery; the *global* UI structure is already the **information architecture** (nav/layout/menu — a UX-requirements spec) plus the **design system** (the visual contract)
- the **app shell / nav / layout** is itself a slice (often the walking skeleton) — its screen is prototyped the same way; there is no separate global prototype pass
- built from the **design system** so prototype and code share one source of truth — no bespoke styling
- **every interaction state** present, not just the happy screen
- self-contained HTML (CDN ok); no build step to click through it

## Output
Written under `prototypes/ui/` (repo root, a non-spec zone):

| File | Captures | Format |
|---|---|---|
| `<screen>.html` | the slice's screen: real components + tokens · all interaction states · wired into the IA's navigation · linked to `UC-`/`DS-` IDs | self-contained HTML |
| `flows.md` | per journey: the screen → screen path, mapped to its `UC-` IDs | journey · screens · UC- |

(generated per UI slice; the screens accrete as UI slices are built — the global structure is the UX-requirements IA + the design system, not a separate pass; no spec changes)
Consumes: the UX requirements (the slice's journey · its IA placement · interaction states), the design system (tokens · components), and the slice's use-cases.

## Excludes
a global pre-built screen gallery (not needed — structure = the IA spec + the design system; the shell is a slice) · production code (→ implementation) · the design-system *definition* and the UX *requirements* (→ the UX requirements) · throwaway empirical spikes (those are disposable; this is the **kept** reference, regenerated from the spec)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
