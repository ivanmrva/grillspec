---
name: grill-design-system
description: >-
  Pin the design system as a spec — design tokens (DTCG, primitive→semantic→component), components-as-contracts (variants · states · ARIA), implementation mapping, accessibility baked into the tokens, brand & assets, and voice/content. Provided, partial, or generated from a brand seed. Use when you need the design system specified, not the journeys. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: a brand seed, an existing token set / design handoff, or a repo
---

# grill-design-system

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **the design system as a spec** — tokens, components, implementation mapping, accessibility-by-construction, brand/assets, and voice — the visual + interaction contract both the prototypes and the code build against.

## Method  (the design system is a swappable input — resolve it tri-mode)
1. **provided** — a ready-made design system (a design-tool handoff bundle, *or* tokens already in the codebase: CSS custom properties · Tailwind config · `design-tokens.json`) → it is the **base**: it lands in the repo's non-spec **`design-system/` zone** (lifted as-is, or normalised to DTCG — the project's call), **kept authoritative where given**, and is the asset **code consumes**. Then **grill on top of it**: **verify & gap-fill against the checklist below** (never skip — a handoff is rarely complete). Your output is a **thin contract over that base, not a copy of it** (see the Rules).
2. **partial** — only some exists (a brand guide, a few tokens) → **extend** to a full system, keeping what's given authoritative
3. **none** — **generate** from the **brand seed** (resolve an open visual *direction* with a throwaway prototype first)
4. in every mode: elicit the **irreducible brand inputs**, generate the rest, and surface each aesthetic call as a **ratify-a-default** HITL (you approve; you don't author)

## Rules
- **the asset is the source of truth code consumes; this spec is a thin contract OVER it, never a copy** — the `design-system/` zone (DTCG/CSS tokens + components + raw brand assets) is what implementation builds from; `design-system.md` holds only the **`DS-` id catalog + the variant/state/ARIA contracts + the a11y verification + a `provided|generated` mark per element**, and **points at** the asset. It must **not** re-list the raw tokens/components in prose — that duplicates the asset and drifts from it. The `DS-` ids are the spec-referenceable glue (a ux journey cites `DS-Card`, a task builds against `DS-Button`); the asset is the substrate they resolve to. On an asset change, **re-verify** — the spec is derived from and checked against the asset, so the two can't disagree. (`provided|generated` is a *source-authority* mark — your irreducible brand vs a ratified default — a timeless property, not edit history.)
- **tokens are the single source, in W3C DTCG JSON** (the latest stable format), **three tiers primitive → semantic → component** — code consumes **semantic/component, never primitives or raw values** — transformed to the platform (CSS custom properties / Tailwind theme via Style Dictionary or equiv.); sets cover colour (primitive ramps → semantic roles bg/surface/text/border/intent + states, incl. **light/dark** so theming is a token swap) · type · spacing · radii · border · elevation · z-index · opacity · sizing · motion · breakpoints · a focus-ring token
- **a component is a contract, not a picture** — per component: anatomy/slots · variant × size matrix · props/API · every state (default/hover/focus/active/disabled/loading/error/empty) · the **WAI-ARIA** keyboard/interaction pattern (interactive ones) · content rules · a canonical reference example · do/don't
- **accessibility by construction** — contrast computed on the actual **token pairs** (target = the quality WCAG level) · **target size ≥ 24×24 CSS px** carried as a minimum-hit-target **sizing token** so it's enforced structurally · **focus appearance** carried by the focus-ring token · reduced-motion · colour never the sole signal · RTL/logical-properties + text-expansion tolerance
- **implementation mapping** — the component strategy (headless lib + tokens · a kit like shadcn/ui · bespoke); each component → its library/bespoke target; the token-build wiring
- **user-provided vs generated** — irreducibly the user's (ask or ratify): brand identity (logo · colour seed · branded typeface · personality + voice principles · product name) · any existing brand guide or codebase tokens · hard brand/legal constraints (exact hexes · font licensing) · the WCAG target. Generated (Claude derives, human ratifies the aesthetic): colour ramps + semantic mappings + dark mode · the type/spacing/radii/elevation/motion scales · component specs + states · a11y defaults · the DTCG token file + transform + examples. A missing item is generated/elicited, or — if a visual/aesthetic call — surfaced as a ratify-a-default HITL
- **brand, assets & voice are part of the system** — logo · identity · favicon/app-icon/OG · illustration & imagery · iconography; and voice/tone + error/empty/confirmation microcopy + date/number/currency/capitalisation formatting

## Output
**Stable IDs** (bare type prefix, ID = the leading table column / row key): `DS-` design-system element (token · component · voice term).
Written under `requirements/design-system/`:

| File | Captures | Format |
|---|---|---|
| `design-system.md` | the design-system spec (DS- ids): tokens (DTCG, primitive→semantic→component) · components (variant×size×state + ARIA) · implementation mapping · accessibility (token-pair contrast · sizing/focus tokens) · brand & assets · voice | DS-id · structured fields |
| `glossary.md` | the design-system lexicon (UI voice · terminology · DS- term names) — distinct from the domain glossary | term · definition |

ADRs → `adr/ADR-DS-NNN.md`
(the token **asset** itself — the DTCG file + raw brand assets — lives in the repo's non-spec `design-system/` zone; this area is its spec and points at it)
Consumes: the brand seed / any provided tokens, the quality usability/WCAG NFRs (the a11y target), and the global glossary (terminology).

## Excludes
pixel-perfect comps + the **act** of visual design execution (the Figma/design-tool work itself → a designer) · journeys · information architecture · journey-level accessibility & usability targets (→ the UX requirements) · **slice-specific** UX — a single screen's mockup/microcopy (→ the task, built against this system) · the clickable prototype that renders these components (→ the UI prototype)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
