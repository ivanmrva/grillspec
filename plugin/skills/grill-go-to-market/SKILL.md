---
name: grill-go-to-market
description: >-
  Pin the go-to-market execution — ICP, channels & per-channel messaging, launch plan, partnerships — aligned to the product's chosen go-to-market motion. Use when you need a GTM plan; late/parallel and optional, not part of the core system spec. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-go-to-market

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Go-to-market** — how customers find, buy, and launch onto it.

## Method
- For each channel, derive its **channel-economics** — expected CAC / payback — and sanity-check it against the deal's **ACV band**: a high-touch channel under a low ACV (or the reverse) is a mismatch to flag.
- Structure the launch as **tiered launches** (e.g. soft → limited → GA), each with its own trigger/criteria, channels, enablement, and readiness gate — not one monolithic event.
- When the motion is **PLG or hybrid**, define the **PQL → sales hand-off**: the qualifying signal and the threshold at which a product-qualified lead is routed to sales.

## Rules
- **late/parallel and optional** — this is not part of the core system spec; don't gate the build on it (the build-shaping **motion** decision lives upstream, in the product vision)
- the primary channel must be consistent with the target segment and the chosen motion
- each channel's expected CAC / payback must clear an **ACV-band sanity check** vs the motion — name the mismatch where it fails

## Output
Written under `commercial/go-to-market/`:

| File | Captures | Format |
|---|---|---|
| `channels.md` | ICP (ideal customer profile) + channels + per-channel messaging (from the positioning statement) + per-channel economics (expected CAC · payback · ACV-band fit) | typed fields |
| `launch.md` | tiered launches | tier · trigger/criteria · channels · enablement · readiness gate |
| `partnerships.md` | partnerships | partner · type[tech/channel/co-sell] · value-exchange · motion-fit |

ADRs → `adr/ADR-GTM-NNN.md`
Consumes: the positioning statement (per-channel messaging derives from it) + the go-to-market motion (channels must fit PLG vs sales-led; PLG/hybrid requires the PQL→sales hand-off).

## Excludes
the **motion** decision itself — PLG vs sales-led is a build-shaping product-strategy fork (→ the product vision) · the system spec — none of this is implementation (→ the architecture) · marketing-asset production

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
