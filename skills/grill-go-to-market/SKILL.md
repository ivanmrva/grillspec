---
name: grill-go-to-market
description: >-
  Plan the go-to-market execution: the ideal customer profile, channels with their messaging,
  the launch sequence and partnerships, aligned to the product's chosen motion. An optional
  commercial area; use only when the user asks for launch or channel planning.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-go-to-market

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Go-to-market** — how customers find, buy, and launch onto it.

Run this only when the user asks for it; nothing in the build path depends on it. The one go-to-market decision that shapes the build, the motion, is made in the product vision.

## Depth by profile
Optional at every profile. Capture what the user will use:

- By default, the ideal customer profile, the primary channel with its message, and the launch sequence.
- Secondary channels and per-channel economics, when the user is planning spend.
- Partnerships and the product-qualified-lead hand-off, when the product has partners or a sales team.

## Rules
- The primary channel is consistent with the target segment and the chosen motion.
- Per-channel messaging derives from the positioning statement where one exists, otherwise from the value proposition.
- Where channel economics are captured, state each channel's expected CAC and payback and check them against the deal's ACV band. A high-touch channel under a low ACV, or the reverse, is a mismatch to name.
- Structure the launch as tiers (soft → limited → GA). Each tier has its own trigger, channels, enablement and readiness gate, so the launch is a sequence of decisions and not one event.
- For a PLG or hybrid motion with a sales team, define the PQL → sales hand-off: the qualifying signal and the threshold at which a product-qualified lead is routed to sales.

## Output
Written under `commercial/go-to-market/`:

| File | Captures | Format |
|---|---|---|
| `channels.md` | the ideal customer profile · channels with per-channel messaging · per-channel economics (expected CAC · payback · ACV-band fit) | typed fields |
| `launch.md` | the tiered launch | tier · trigger/criteria · channels · enablement · readiness gate |
| `partnerships.md` | partnerships | partner · type (tech / channel / co-sell) · value-exchange · motion-fit |

ADRs → `adr/ADR-GTM-NNN.md`
Consumes: the positioning statement or value proposition (messaging derives from it) and the go-to-market motion (channels must fit self-serve or sales-led).

## Excludes
the motion decision itself — PLG vs sales-led is a build-shaping product-strategy fork (→ the product vision) · the system spec — none of this is implementation (→ the architecture) · marketing-asset production

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
