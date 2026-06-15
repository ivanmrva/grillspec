# grill-design-system — worked example

**Mode: provided.** A design-tool handoff bundle landed in the repo's `design-system/` zone (CSS custom properties + a partial `design-tokens.json`). Ingested, then verified against the checklist — a handoff is rarely complete, so it gets gap-filled, not trusted wholesale.

> **Claude:** The tokens are present but **single-tier** (raw values, no semantic layer) and **light-only**; there's no focus-ring token, and the Button spec is missing its `loading` and `disabled` states. I restructured to three tiers (primitive → semantic → component), derived a dark theme as a pure semantic swap, added the focus-ring + minimum-hit-target sizing tokens, and completed the Button contract. The brand seed (logo, `#1F6FEB`, voice = "plain, calm") is yours — I kept it authoritative and had you ratify the derived ramps.

`requirements/design-system/design-system.md` (one component, abridged):
```
DS-Button  (component-tier token consumer)
  anatomy: [icon?] label [icon?]        variants × sizes: {primary,secondary,ghost,danger} × {sm,md,lg}
  states:  default · hover · focus · active · disabled · loading · empty(N/A) · error(N/A)
  api:     variant, size, leadingIcon?, trailingIcon?, loading, disabled, onPress
  a11y:    role=button · focus-visible ring = token focus.ring (3:1 vs adjacent) · hit-target ≥ size.target.min (24px)
           contrast: text.on-intent / bg.intent.primary = 4.8:1  (≥ the WCAG-target ratio on the *actual* token pair)
  tokens:  bg=color.bg.intent.{variant} · text=color.text.on-intent · radius=radius.control · motion=motion.press
  do: one primary action per view.    don't: encode meaning in colour alone — pair with icon/text.
```
The token **asset** stays under the repo-root `design-system/` zone (the DTCG JSON, transformed via Style Dictionary → CSS vars); this spec is its contract and points at it.

DS- ids the UI prototype and the build consume: `DS-Button`, `DS-Input`, `DS-Banner` · semantic tokens `color.*`, `focus.ring`, `size.target.min`. A journey that uses these (nav, states, flow) is the **UX requirements'** concern, not this area's.
