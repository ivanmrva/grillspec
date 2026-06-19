---
name: grill-ux-reqs
description: >-
  Pin the UX requirements — per-role journeys with their interaction states, information needs (the information architecture), and accessibility & i18n targets. Use when you need UX requirements, not the design system or visual design. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-ux-reqs

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **UX requirements** — journeys, per-role information needs, the information architecture, and accessibility/i18n. The design system (tokens · components · brand · voice) is a **separate area**; journeys reference it as a given input.

## Rules
- every journey carries its **interaction states** (empty · loading · success · error · permission-denied) — this is where the functional spec's "what does the user see on rejection" gaps land
- **every journey clears the journey-level accessibility bars** (current success-criteria): **accessible authentication** — no cognitive-function test (memorizing, transcribing, puzzle-solving) on any auth/critical step; an accessible alternative always exists · **consistent help** — help/support access in the same relative place across the journey · **dragging-movements** — any drag interaction has a single-pointer (non-drag) alternative
- **inclusivity** note per journey, **distinct from the WCAG conformance level** — cognitive load kept low · plain language · tolerant of situational/temporary impairment (one-handed, bright sun, noisy room); broader than conformance, not a substitute for it
- for an open UX *direction* (which flow/layout), resolve it with a **throwaway prototype** (toggleable variants) rather than guessing — the chosen direction becomes the requirement
- **the journey is rendered in the design system, not redefined here** — reference its components/tokens by `DS-` id; a missing component is a **gap raised to the design-system area**, not invented in a journey

## Output
Written under `ux/`:

| File | Captures | Format |
|---|---|---|
| `journeys.md` | per role: user journeys with required interaction states (empty/loading/success/error/permission-denied) | role · numbered steps · states |
| `information-needs.md` | per-role information needs + information architecture (screen inventory + navigation map) | role · bullets |
| `accessibility.md` | accessibility (concrete WCAG level, incl. target-size/focus-appearance/accessible-auth/consistent-help/dragging-alternative bars) + an **inclusivity** target distinct from the conformance level (cognitive load · plain language · situational impairment) + i18n/l10n targets + per-critical-journey usability targets framed as **effectiveness · efficiency · satisfaction**, each with a **named measurement instrument** (e.g. task-completion rate · time-on-task/SEQ · SUS), tied to the quality usability NFRs | target · instrument · list |

ADRs → `adr/ADR-UX-NNN.md`
Consumes: the functional spec (its rejection/state gaps), the domain read-models + actors (task + information needs per role), the **design system** (its tokens · components — journeys reference them by `DS-` id), the global glossary (terminology), the quality usability/WCAG NFRs (targets), and the go-to-market motion (onboarding differs for self-serve vs sales-led).

## Excludes
the **design system** (tokens · components · brand · voice → its own area) · pixel-perfect comps + the **act** of visual design execution (the Figma/design-tool work itself → a designer) · **slice-specific** UX — a single task's mockup/microcopy/states is produced when the task is finalized and recorded in the task; this area owns the **global** UX (journeys · IA · journey-level a11y)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
