---
name: grill-design-system
description: >-
  Pin the design system as a spec: design tokens in three tiers, components as contracts with
  variants, states and ARIA, accessibility built into the tokens, brand assets and voice, from a
  provided system or a brand seed. Use for a product with a UI.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-design-system

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **the design system as a spec** — tokens, components, implementation mapping, accessibility-by-construction, brand/assets, and voice — the visual + interaction contract both the prototypes and the code build against.

## Depth by profile
This area exists only for a product with a UI. At `regulated` the readiness gate expects the area, so a product without one records `N/A — <why>` in `design-system.md`.

| Profile | What the interview captures |
|---|---|
| `lite` | not a separate area. |
| `standard`, `regulated` | the contract over the token and component asset: the `DS-` catalogue, each component's variants, states and ARIA pattern, and the contrast check on the real token pairs. Keep the prose short, because the asset holds the values. Brand, asset and voice entries stay to a few lines unless the brand is what differentiates the product. |

## Method
The design system is a swappable input. Start from what exists.

| What exists | What to do |
|---|---|
| provided: a design-tool handoff, or tokens already in the codebase (CSS custom properties · Tailwind config · `design-tokens.json`) | It is the base. It lands in the repo's `design-system/` zone as given or normalised to DTCG (the project's call), stays authoritative where it speaks, and is what code consumes. Verify it against the rules below and fill the gaps; a handoff is rarely complete. |
| partial: a brand guide, a few tokens | Extend it to a full system and keep what is given authoritative. |
| none | Generate the system from the brand seed. Settle an open visual direction with a throwaway prototype first. |

In every case, ask for the brand inputs only the user holds, generate the rest, and present each aesthetic call as a default for the user to ratify.

## Rules
- **Asset and spec.** The `design-system/` zone (DTCG or CSS tokens, components, raw brand assets) is the source of truth that code consumes. `design-system.md` is a thin contract over it: the `DS-` catalogue, the variant, state and ARIA contracts, the accessibility verification, and a `provided` or `generated` mark per element. It points at the asset and leaves the raw token values there, because a copy drifts from the asset. When the asset changes, re-verify the spec against it.
- **`DS-` ids** are what the rest of the spec cites: a journey cites `DS-Card`, a task builds against `DS-Button`. The `provided | generated` mark records source authority: the user's own brand, or a default the user ratified.
- **Tokens.** One source, in W3C DTCG JSON (the latest stable format), in three tiers: primitive → semantic → component. Code consumes semantic and component tokens, so a theme is a token swap; a primitive or a raw value in code bypasses theming. Tokens are transformed to the platform (CSS custom properties or a Tailwind theme, through Style Dictionary or an equivalent).
- **Token sets.** Colour (primitive ramps → semantic roles for background, surface, text, border and intent, with states, in light and dark) · type · spacing · radii · border · elevation · z-index · opacity · sizing · motion · breakpoints · a focus-ring token.
- **A component is a contract.** Per component: anatomy and slots · the variant × size matrix · props/API · every state (default · hover · focus · active · disabled · loading · error · empty) · for an interactive component, its WAI-ARIA keyboard and interaction pattern · content rules · one reference example · do and don't.
- **Accessibility by construction.** Contrast is computed on the actual token pairs, against the WCAG level the quality requirements set. The minimum target size (24×24 CSS px) is a sizing token and focus appearance is the focus-ring token, so both are enforced structurally. The system also covers reduced motion, colour not being the only signal, RTL through logical properties, and tolerance for text expansion.
- **Implementation mapping.** The component strategy (a headless library plus tokens · a kit such as shadcn/ui · bespoke), each component's library or bespoke target, and the token-build wiring.
- **Provided by the user** (asked for or ratified): brand identity (logo · colour seed · branded typeface · personality and voice principles · product name), any existing brand guide or codebase tokens, hard brand or legal constraints (exact hexes · font licensing), and the WCAG target.
- **Generated for the user to ratify:** colour ramps, semantic mappings and dark mode · the type, spacing, radii, elevation and motion scales · component specs and states · accessibility defaults · the DTCG file, its transform and the examples.
- **Brand, assets and voice** are part of the system: logo · favicon, app icon and social image · illustration, imagery and iconography · voice and tone · error, empty and confirmation microcopy · date, number, currency and capitalisation formats.

## Output
**IDs:** `DS-` design-system element (token · component · voice term).
Written under the design-system spec area, which is its own layer. The raw tokens and brand assets live in the repo's non-spec `design-system/` zone; this area is their contract and points at them.

| File | Captures | Format |
|---|---|---|
| `design-system.md` | the `DS-` catalogue: tokens by tier · components (variant × size × state + ARIA) · implementation mapping · accessibility (token-pair contrast · sizing and focus tokens) · brand and assets · voice | one entry per `DS-` id, as structured fields |
| `glossary.md` | the design-system lexicon: UI voice and terminology, distinct from the domain glossary | term · definition |

In `glossary.md` the term leads the row. A term that names a `DS-` element cites the id after it, because the element is defined in `design-system.md`.

ADRs → `adr/ADR-DS-NNN.md`
Consumes: the brand seed or any provided tokens, the quality requirements' usability and WCAG targets (the accessibility bar), and the domain glossary (terminology).

## Excludes
pixel-perfect comps and the act of visual design execution (the design-tool work itself → a designer) · journeys · information architecture · journey-level accessibility & usability targets (→ the UX requirements) · slice-specific UX — a single screen's mockup or microcopy (→ the task, built against this system) · the clickable prototype that renders these components (→ the UI prototype)

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
