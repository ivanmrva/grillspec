---
name: grill-market
description: >-
  Map the competitive landscape — direct competitors in a comparison matrix, indirect alternatives incl. status-quo/DIY, defensible differentiation with named moats, switching costs, and order-of-magnitude sizing. Feeds positioning and the viability bet. Use when you need the landscape and rough size mapped, not a financial model. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-market

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Market & competitive landscape** — who else solves this, why we win, and how big it is.

## Rules
- name **both** direct competitors and indirect alternatives (incl. the status quo — what people do today)
- differentiation must be **defensible** — back it with named **moats** (network-effects · switching-cost · scale · brand · IP · data), each with **evidence + status** and a **time/cost to replicate**, plus the switching costs that protect it
- sizing is **bottom-up** — build SOM from **ACV × reachable-ICP-count**, use a top-down estimate only as a sanity check, and note the **method + key assumption per layer**; order-of-magnitude, not a financial model
- weigh **structural attractiveness** — the threat of new entrants, substitutes, and the bargaining power of buyers and suppliers, plus rivalry; a big market is unattractive if the forces are hostile

## Output
Written under `product/market/`:

| File | Captures | Format |
|---|---|---|
| `competitors.md` | direct competitors × the 3–4 axes that matter (comparison matrix) + indirect alternatives & status-quo/DIY | comparison matrix |
| `industry-forces.md` | structural attractiveness of the market | new-entrant threat · substitutes · buyer power · supplier power · rivalry · ecosystem note |
| `differentiation.md` | why us, defensibly + named moats, each evidenced & hard to copy | moat (network-effects · switching-cost · scale · brand · IP · data) · evidence/status · time/cost to replicate |
| `sizing.md` | bottom-up sizing, top-down as a check | SOM = ACV × reachable-ICP-count · TAM/SAM as context · method + key assumption per layer · order-of-magnitude |

ADRs → `adr/ADR-MKT-NNN.md`

## Excludes
pricing · go-to-market channels · detailed features

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
