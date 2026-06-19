---
name: generate-ui-prototype
description: >-
  Generate a clickable HTML prototype of the screen(s) a UI slice implements — built from the real design-system tokens & components, with every interaction state, wired into the navigation the information architecture defines — as the precise visual + interaction reference the coding task builds against. Produced when a ux-heavy slice is finalized (the design-review window), not in the coding loop; skipped when the IA + design system already determine the screen. Loads the shared exec core.
disable-model-invocation: true
argument-hint: the UI slice (its screen[s], from the UX requirements + design system)
---

# generate-ui-prototype

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **a clickable HTML prototype of the screen(s) a UI slice implements** — the exact reference the coding task builds against (kept + versioned, not a throwaway spike). It is produced **when the task is finalized** — the human design-review/tweak window — then **frozen into the task**; the coding step (later, possibly unattended) builds against it.

## When it runs (and when it doesn't)
- **Produced at task finalization, before the build run — not inside the coding loop.** Finalization is the attended, batched step where you review + tweak the screen and freeze it; an AFK build then runs against the frozen prototype and never breaks to show you a screen. A tweak that arrives once code is flowing is too late by design — the window is here.
- **Not obligatory.** A prototype earns its place only when the slice has **slice-specific composition** to pin (a new screen/flow, non-obvious states). A slice the **IA + design system already fully determine** (existing components, obvious composition — a copy change, a field added to an existing form) needs **none**; that slice marks its `ux` dimension `N/A — reuses DS-… on the existing screen`. Same opt-in logic as `derive-impl-design` (design-first slices only).
- **Reaches autorun without one? Generated JIT, then built against — no pause.** A UI slice that enters the autorun queue with no frozen prototype (you chose not to pre-review it) has one generated just-in-time and builds against it unattended — you still get the prototype as the build reference and an after-the-fact record, you just forgo the review-first window (autorun is unattended by definition). To *review* a specific screen first, simply **don't finalize/queue that slice** until you have — withholding it from the queue is the review gate; no separate flag exists or is needed.

## Process
1. **Take the slice's screen(s)** from the UX requirements — the journey step, its place in the information architecture, and its required interaction states.
2. **Render each screen** from the **real design-system tokens & components** (semantic/component tokens, the actual component variants/states — never ad-hoc styling), covering every interaction state (empty · loading · success · error · permission-denied).
3. **Wire it into the navigation** the IA defines (so it clicks through in context); cross-link the screen to its `UC-`/`DS-` IDs.
4. **Freeze it into the task** as the `ux` resolution; **regenerate** on a UX/design-system change (propagation re-flags it) — it's a projection, not hand-maintained.

## Rules
- **per-slice, at finalization** — generated for the screen(s) of the slice being finalized, not as a global pre-built gallery; the *global* UI structure is already the **information architecture** (nav/layout/menu — a UX-requirements spec) plus the **design system** (the visual contract)
- the **app shell / nav / layout** is itself a slice (often the walking skeleton) — its screen is prototyped the same way; there is no separate global prototype pass
- built from the **design system** so prototype and code share one source of truth — no bespoke styling; a missing component is a **gap raised to the design system**, never invented here
- **every interaction state** present, not just the happy screen
- self-contained HTML (CDN ok); no build step to click through it

## Output
Written under `prototypes/ui/` (repo root, a non-spec zone):

| File | Captures | Format |
|---|---|---|
| `<screen>.html` | the slice's screen: real components + tokens · all interaction states · wired into the IA's navigation · linked to `UC-`/`DS-` IDs | self-contained HTML |
| `flows.md` | per journey: the screen → screen path, mapped to its `UC-` IDs | journey · screens · UC- |

(generated per ux-heavy UI slice at its finalization; the screens accrete as UI slices are finalized — the global structure is the UX-requirements IA + the design system, not a separate pass; no spec changes)
Consumes: the UX requirements (the slice's journey · its IA placement · interaction states), the design system (tokens · components), and the slice's use-cases.

## Excludes
a global pre-built screen gallery (not needed — structure = the IA spec + the design system; the shell is a slice) · production code (→ implementation) · the design-system *definition* and the UX *requirements* (→ the UX requirements) · throwaway empirical spikes (those are disposable; this is the **kept** reference, regenerated from the spec)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
