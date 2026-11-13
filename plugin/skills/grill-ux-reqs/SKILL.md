---
name: grill-ux-reqs
description: >-
  Pin the UX requirements: the screen inventory, per-role journeys with their interaction states,
  and the accessibility and i18n targets. Use for a product with a UI when you need what each
  journey and screen must do, not the design system or visual design.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-ux-reqs

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **UX requirements** — journeys, per-role information needs, the information architecture, and accessibility/i18n. The design system (tokens · components · brand · voice) is a separate area; journeys cite it as a given input.

## Depth by profile
This area exists only for a product with a UI. At `regulated` the readiness gate expects the area, so a product without one records `N/A — <why>` in `journeys.md`.

| Profile | What the interview captures |
|---|---|
| `lite` | not a separate area. |
| `standard`, `regulated` | the screen inventory, the journeys with their interaction states, and the accessibility level with the journey-level bars. Keep the prose short: a journey is numbered steps and one line per state. |
| `regulated`, or where the product has the concern | usability targets with a named instrument, when the team will run usability tests. i18n/l10n targets, when the product ships in more than one locale. |

## Rules
- Every journey carries a stable `JRN-` id (`JRN-07`) as the first token of its heading or row. Tasks and tests cite the journey by id, because a heading anchor breaks when the heading is reworded.
- Every journey cites the `UC-` use-case or use-cases it renders, on that same heading or row. A journey is the rendering of a use-case; one with no use-case behind it is a gap to raise, not a requirement to invent here. The exception is a journey that renders a Generic subdomain deliberately left unmodelled (passwordless sign-in, plan and billing management), which declares `N/A — renders <Generic subdomain>, unmodeled`.
- Every journey carries its interaction states: empty · loading · success · error · permission-denied. This is where the functional spec's "what does the user see on rejection" gaps are settled.
- Every journey clears three journey-level accessibility bars. Accessible authentication: an authentication or critical step has a path with no cognitive-function test (memorising, transcribing, solving a puzzle). Consistent help: help sits in the same relative place across the journey. Dragging: every drag interaction has a single-pointer alternative.
- Inclusivity is broader than a conformance level: low cognitive load, plain language, and tolerance of situational impairment (one hand, bright sun, a noisy room). State the target once in `accessibility.md`, and add a note to a journey only where it has a specific constraint.
- Settle an open UX direction (which flow, which layout) with a throwaway prototype with toggleable variants. The chosen direction becomes the requirement.
- A journey is rendered in the design system. Cite components and tokens by `DS-` id; a missing component is a gap raised to the design-system area.
- Every screen the information architecture names carries an `SCR-` id, so a journey step, a task and a prototype file anchor to the screen and not to a prose name.

## Output
**IDs:** `JRN-` journey · `SCR-` screen.
Written under `ux/`:

| File | Captures | Format |
|---|---|---|
| `journeys.md` | per role, the journeys with their interaction states; each step names the screen it happens on | `JRN-` id · role · serves(`UC-`) · numbered steps (`SCR-` per step) · states |
| `information-needs.md` | per-role information needs and the information architecture: the screen inventory and the navigation map drawn over it | table keyed on `SCR-`: purpose · primary role(s) · journeys that touch it; then the navigation map |
| `accessibility.md` | the WCAG level, including the target-size, focus-appearance and journey-level bars · the inclusivity target · i18n/l10n targets · usability targets | target · instrument |

A screen that no journey or task references is dead information architecture, and the linter warns on it. In `journeys.md` a step cites its screen after the step text; the `SCR-` id leads a row only in the inventory, where the screen is defined.

Usability targets are set per critical journey as effectiveness · efficiency · satisfaction, each with a named instrument (task-completion rate · time-on-task or SEQ · SUS) and tied to the quality requirements' usability targets. The brief of a UI task takes the WCAG criteria, keyboard path and i18n targets for its screen from `accessibility.md`.

ADRs → `adr/ADR-UX-NNN.md`
Consumes: the functional spec (its rejection and state gaps), the domain read models and actors (the tasks and information each role needs), the design system (cited by `DS-` id), the domain glossary (terminology), the quality requirements' usability and WCAG targets, and the go-to-market motion (onboarding differs between self-serve and sales-led).

## Excludes
the design system (tokens · components · brand · voice → its own area) · pixel-perfect comps and the act of visual design execution (the design-tool work itself → a designer) · slice-specific UX — a single task's mockup, microcopy and states are produced when the task is finalised and recorded in the task; this area owns the global UX (journeys · information architecture · journey-level accessibility)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
