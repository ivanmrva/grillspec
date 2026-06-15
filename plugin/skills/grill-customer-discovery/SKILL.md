---
name: grill-customer-discovery
description: >-
  Pin who the product is for — target market & segments, personas with the B2B decision-making unit, and the jobs-to-be-done behind each. Flags which personas are system users, seeding the shared actor roster. Use when you need the primary segment, its JTBD, and the personas nailed. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-customer-discovery

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Customer & market discovery** — the segments, personas, and jobs-to-be-done.

## Rules
- the **primary segment and its JTBD** lead — secondary segments only once that's clear
- **decompose each JTBD**: a job statement ("when <situation>, I want <motivation>, so I can <outcome>") + its functional / emotional / social dimensions + the desired outcomes — not a one-line task
- personas are **behavioral, not demographic** — carry observed behaviors, each tagged with **evidence/source** and flagged **hypothesis vs interview-grounded**
- for B2B, capture the **decision-making unit** (user · buyer · economic-buyer · champion/influencer), and flag each persona as a **system user** vs a purely **buying role**

## Output
Written under `product/customers/`:

| File | Captures | Format |
|---|---|---|
| `segments.md` | one block per target segment | name · JTBD decomposed (job statement: when…/I want…/so I can… · functional/emotional/social · desired outcomes) · key traits |
| `icp.md` | the targeting criteria that define the ideal customer | firmographics/behaviors · why-primary = attractiveness × reachability × fit |
| `personas.md` | personas as typed fields — behavioral, sourced | behaviors + evidence/source · goals · context · pains · hypothesis vs interview-grounded |
| `actors.md` | personas flagged as system users — the product-lens actor source | — |

ADRs → `adr/ADR-CUST-NNN.md`

## Excludes
UX journeys · system actors' command-level permissions · go-to-market

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
