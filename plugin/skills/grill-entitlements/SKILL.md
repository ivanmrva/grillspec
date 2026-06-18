---
name: grill-entitlements
description: >-
  Pin the entitlement model — the access tiers, what each unlocks (feature gating), usage limits/quotas, and how access degrades on a lapsed billing state — as the access-control contract architecture enforces. The STRUCTURAL half of monetization (pricing is a separate commercial area). Loads the shared grill engine.
disable-model-invocation: true
argument-hint: the functional features to gate, an existing plan matrix, or a repo
---

# grill-entitlements

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **the entitlement model** — the abstract access tiers, the tier×capability grid (feature gating), usage limits/quotas, and billing-state degradation — the access contract the architecture builds against. It is **upstream of the architecture gate** because the code enforces it. Pricing, plans-as-revenue, and unit economics are a **separate commercial area**; this owns *who can access what*, not *what it costs*.

## Method  (derive the grid from features, elicit the gating policy)
1. **derive** the candidate tier×capability grid from the **functional features** (each `UC-` is a gatable capability) and any provided plan matrix
2. **elicit** the gating decisions only the business holds: which capabilities are gated vs always-on, the **tiers** (by capability, not price), per-capability **limits/quotas**, and the **over-limit** and **billing-state** behaviour
3. surface each gating call as a **ratify-a-default** HITL where a sensible default exists (gate the premium capability, soft-cap the limit)

## Rules
- **a tier is defined by capability, never by price** — abstract access levels (e.g. Free · Pro · Enterprise) whose *meaning* is the set of capabilities + limits they grant; the **price** of a tier lives in the commercial **monetization** area and references these tiers, never the reverse (so entitlements stay upstream of pricing)
- **every entitlement names**: the capability gated (by `UC-` / feature id), the **tier(s)** that grant it, the **limit/quota** (or "unlimited"), the **over-limit behaviour** (block · soft-cap · grace-then-block), and the **enforcement boundary** (where the check lives) — so it is implementable as authorization
- **entitlements are an access grant** — code consumes them like authorization (an entitlement is a permission source); they **plug into** the security authz model, they don't redefine it (role-based authz → security area)
- **billing-state degradation** — define how access changes on **lapse / dunning / grace / cancellation**: which capabilities **retain** (read-only, data export) vs **revoke**, and the grace window — so a non-paying state has a specified, not improvised, access surface
- **no orphan capability** — a functional feature with no entitlement decision (gated or always-on) is a **gap**, not a silent default

## Output
**Stable IDs** (bare type prefix, ID = the leading table column / row key): `ENTL-` an entitlement (a gated capability + its tier grant + limit).
Written under `requirements/entitlements/`:

| File | Captures | Format |
|---|---|---|
| `entitlements.md` | the tier×capability grid (`ENTL-` ids): capability (`UC-` ref) · granting tier(s) · limit/quota · over-limit behaviour · enforcement boundary · billing-state degradation | `ENTL-` id · structured fields · a tier×capability table |

ADRs → `adr/ADR-ENTL-NNN.md`
Consumes: the **functional spec** (the `UC-` capabilities to gate), the **domain** (capabilities + actors), and the **security** authz model (the access mechanism entitlements plug into). The **architecture** consumes this to build feature-gating, quota enforcement, and billing-state access.

## Excludes
**pricing · plans-as-revenue · unit economics · the billing model** (PLG vs sales-led) → the commercial **monetization** area (it reads these tiers and attaches prices) · the **role/permission authz model** → **security** · billing-integration mechanics (Stripe wiring, invoicing) → the **solution** · the go-to-market motion → **product-vision**

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
