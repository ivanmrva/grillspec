---
name: grill-problem-validation
description: >-
  Pin the problem worth solving and score the riskiest bets — problem hypothesis (who hurts, how badly, vs which alternatives, why-now), desirability/viability/feasibility bets scored criticality × uncertainty, value-proposition fit, and a PMF definition with the cheapest test per assumption. Runs first and never closes. Use when you need the problem nailed and the riskiest bets scored before anything is built. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-problem-validation

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Problem validation & discovery** — the problem worth solving and the riskiest bets behind it.

## Rules
- **every critical bet carries a validation status + a falsifiable test plan** — a prediction with a pass/fail threshold, not a hope
- pain is **frequency × intensity, painkiller vs vitamin** — and name the **why-now / catalyst**, or it isn't urgent
- weigh the **forces around a switch** — push of the problem + pull of the new way vs anxiety of switching + habit of today; the solution wins only when push+pull beat anxiety+habit
- you **plan** validation, you don't run it — the real test happens in the market (cheapest test per risky assumption)
- kill-criteria are referenced, not authored here

## Output
Written under `discovery/`:

| File | Captures | Format |
|---|---|---|
| `problem.md` | problem hypothesis + the forces driving (or blocking) a switch | who hurts · frequency × intensity · current alternatives · why-now · demand-forces (push · pull · anxiety · habit) |
| `opportunities.md` | distinct unmet needs/pains under the target outcome | opportunity · evidence · reach · severity |
| `bets.md` | riskiest desirability/viability/feasibility bets, scored, with status | bet · type · criticality · uncertainty · status |
| `assumptions.md` | assumptions register — each status change traceable to a datapoint | # · assumption · type · criticality · uncertainty · status · evidence/source (snippet/quote/datapoint · source · date) · test-plan |
| `value-prop-fit.md` | value-prop fit, 2-col | jobs/pains/gains ↔ pain-relievers/gain-creators |
| `pmf.md` | PMF signal **cluster** + validation plan — no single signal stands alone | per signal: signal · target · cheapest falsifiable test — incl. the "% very disappointed" survey, retention-curve flattening, and a qualitative signal |

ADRs → `adr/ADR-PROB-NNN.md`

## Excludes
the validation itself (happens in the market) · the product spec (downstream) · success metrics & kill-criteria (→ goals)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
