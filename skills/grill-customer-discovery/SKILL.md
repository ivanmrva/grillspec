---
name: grill-customer-discovery
description: >-
  Pin who the product is for: the target segments, behavioural personas with the B2B buying roles,
  and the job-to-be-done behind each. An optional strategy area; use only when the user asks for
  segment or persona work.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-customer-discovery

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Customer & market discovery** — the segments, personas, and jobs-to-be-done.

Run this only when the user asks for it; nothing in the build path depends on it. Without it, the product vision's who-it-is-for paragraph is the record of the target user.

## Depth by profile
Optional at every profile. Capture what the user will use:

- By default, the primary segment with its job-to-be-done, and the personas behind it.
- Secondary segments and the scored ideal-customer profile, when the user is choosing between segments.
- The decision-making unit, when the product is sold B2B to a buyer who is not the user.

## Rules
- The primary segment and its job-to-be-done come first. Secondary segments wait until that is clear.
- A job-to-be-done is more than a one-line task. Write the job statement ("when <situation>, I want <motivation>, so I can <outcome>"), its functional, emotional and social sides, and the outcomes the person wants.
- Personas describe behaviour, not demographics. Each observed behaviour carries its evidence or source and is marked hypothesis or interview-grounded, so a reader can tell a finding from a guess.
- For B2B, capture the decision-making unit (user · buyer · economic buyer · champion or influencer) and mark each persona as a system user or a purely buying role. Only system users become actors in the product.

## Output
Written under `product/customers/`:

| File | Captures | Format |
|---|---|---|
| `segments.md` | one block per target segment | name · job statement (when… / I want… / so I can…) · functional / emotional / social · desired outcomes · key traits |
| `icp.md` | the targeting criteria of the ideal customer | firmographics / behaviours · why-primary = attractiveness × reachability × fit |
| `personas.md` | personas as typed fields | behaviours + evidence/source · goals · context · pains · hypothesis vs interview-grounded |
| `actors.md` | the personas that are system users | persona · system user or buying role |

ADRs → `adr/ADR-CUST-NNN.md`
Consumes: the product vision — the product and segment whose personas and jobs this area discovers.

## Excludes
UX journeys · system actors' command-level permissions · go-to-market

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
