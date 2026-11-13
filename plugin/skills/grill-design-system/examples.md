# grill-design-system — worked example

Illustrative: it shows the shape of the output, not a list to fill. A design-tool handoff landed in the repo's `design-system/` zone: CSS custom properties and a partial `design-tokens.json`.

> **Agent:** The tokens are single-tier (raw values, no semantic layer) and light-only. There is no focus-ring token, and Button has no `loading` or `disabled` state. I restructured them into three tiers, derived a dark theme as a semantic swap, added the focus-ring and minimum-target tokens, and completed the Button contract. The logo, the seed colour `#1F6FEB` and the voice ("plain, calm") are yours and unchanged. Do the derived ramps look right?
> **User:** Yes. Make the danger red slightly less saturated.

## Output — `design-system.md` (one component)
```
DS-Button   component · generated from the provided handoff
  anatomy:   [icon?] label [icon?]
  variants:  {primary, secondary, ghost, danger} × {sm, md, lg}
  states:    default · hover · focus · active · disabled · loading
  api:       variant, size, leadingIcon?, trailingIcon?, loading, disabled, onPress
  a11y:      role=button · focus ring = focus.ring (3:1 against adjacent colours)
             hit target ≥ size.target.min (24 px)
             contrast text.on-intent / bg.intent.primary = 4.8:1, measured on the token pair
  tokens:    bg = color.bg.intent.{variant} · text = color.text.on-intent · radius = radius.control
  do:        one primary action per view
  don't:     carry meaning in colour alone; pair it with an icon or text
```

The entry names tokens and leaves their values in the DTCG file under `design-system/`, which Style Dictionary transforms to CSS variables.

Other areas cite `DS-Button`, `DS-Input` and `DS-Banner` by id. How a screen uses them is the UX requirements' concern.
