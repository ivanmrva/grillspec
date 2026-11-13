---
name: grill-problem-validation
description: >-
  Pin the problem worth solving and the risky bets behind it: the problem hypothesis, then each
  desirability, viability and feasibility bet with its criticality, status and cheapest test. Use
  at the start of a product and whenever new evidence changes a bet.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-problem-validation

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Problem validation & discovery** — the problem worth solving and the riskiest bets behind it.

## Depth by profile
In scope at every profile (`lite`, `standard`, `regulated`). Its depth follows the discovery work, not the profile.

| When | What the interview captures |
|---|---|
| always | `problem.md` and `bets.md`: the problem hypothesis, then the bets and how each would be tested. About one page in total. |
| the team is gathering evidence (interviews, prototypes, usage) | the other four files, which track that evidence. A project with no discovery work under way has nothing to put in them. |

## Rules
- A bet is a prediction with a pass/fail threshold. Every `Critical` bet carries a validation status and a falsifiable test, because the readiness gate cannot judge a bet that nothing could disprove.
- Criticality is the closed set `Critical | High | Low`, written as the exact token. The readiness gate and the pivot loop match the literal `Critical`, so a synonym slips past both. Status uses the engine's validation set.
- Size the pain as frequency × intensity (painkiller or vitamin) and name the why-now catalyst. Without a catalyst the problem is not urgent.
- Weigh the forces around a switch: the push of the problem and the pull of the new way, against the anxiety of switching and the habit of today. The product wins only when push + pull beat anxiety + habit.
- Plan the cheapest test for each risky assumption.
- Kill-criteria belong to the goals (at `lite`, to the product vision). Cite them here.

## Output
Written under `discovery/`:

| File | Captures | Format |
|---|---|---|
| `problem.md` | the problem hypothesis and the forces for and against a switch | who hurts · frequency × intensity · current alternatives · why-now · demand forces (push · pull · anxiety · habit) |
| `bets.md` | the risky desirability / viability / feasibility bets | table: bet · type · criticality · uncertainty · status · test |
| `opportunities.md` | distinct unmet needs under the target outcome | opportunity · evidence · reach · severity |
| `assumptions.md` | the assumptions register; each status change traces to a datapoint | # · assumption · type · criticality · uncertainty · status · evidence/source (the quote or datapoint and where it came from) · test-plan |
| `value-prop-fit.md` | value-proposition fit, in two columns | jobs / pains / gains ↔ pain-relievers / gain-creators |
| `pmf.md` | a cluster of product-market-fit signals with a validation plan; no single signal stands alone | per signal: signal · target · cheapest falsifiable test |

A usual `pmf.md` cluster is the "% very disappointed" survey, a retention curve that flattens, and one qualitative signal.

ADRs → `adr/ADR-PROB-NNN.md`

## Excludes
the validation itself (happens in the market) · the product spec (downstream) · success metrics & kill-criteria (→ goals)

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
