---
name: grill-market
description: >-
  Map the competitive landscape: direct competitors in a comparison matrix, indirect alternatives
  including the status quo, defensible differentiation with named moats, and order-of-magnitude
  sizing. An optional strategy area; use only when the user asks for market analysis.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-market

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Market & competitive landscape** — who else solves this, why we win, and how big it is.

Run this only when the user asks for it; nothing in the build path depends on it.

## Depth by profile
Optional at every profile. Capture what the user will use:

- By default, the competitor matrix (including the status quo) and the differentiation with its moats.
- Industry forces and sizing, when the user faces a go/no-go, fundraising or market-entry decision that turns on them.

## Rules
- Name both direct competitors and indirect alternatives. The status quo (what people do today) is usually the real incumbent.
- Differentiation has to be defensible. Back it with named moats (network effects · switching cost · scale · brand · IP · data), each with its evidence, its status, and the time or cost to replicate it.
- Size bottom-up: SOM = ACV × the count of reachable ideal customers. A top-down figure is only a sanity check. Note the method and the key assumption per layer, and stay at order of magnitude; this is not a financial model.
- Weigh structural attractiveness: the threat of new entrants and substitutes, the bargaining power of buyers and suppliers, and rivalry. A big market is unattractive when those forces are hostile.

## Output
Written under `product/market/`:

| File | Captures | Format |
|---|---|---|
| `competitors.md` | direct competitors against the 3–4 axes that matter, plus indirect alternatives and the status quo | comparison matrix |
| `differentiation.md` | why us, defensibly | moat · evidence / status · time or cost to replicate |
| `industry-forces.md` | the structural attractiveness of the market | new-entrant threat · substitutes · buyer power · supplier power · rivalry · ecosystem note |
| `sizing.md` | bottom-up sizing, with top-down as a check | SOM = ACV × reachable-ICP count · TAM / SAM as context · method + key assumption per layer |

ADRs → `adr/ADR-MKT-NNN.md`
Consumes: the product vision — the category and positioning to analyse and size.

## Excludes
pricing · go-to-market channels · detailed features

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
