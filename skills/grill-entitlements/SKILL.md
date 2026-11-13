---
name: grill-entitlements
description: >-
  Pin the entitlement model: access tiers, the tier × capability grid, usage limits with their
  over-limit behaviour, and how access degrades when billing lapses. Use when the product has
  tiers or plans that the code must enforce.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-entitlements

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **the entitlement model** — the abstract access tiers, the tier × capability grid, usage limits, and billing-state degradation. It is the access contract the architecture builds against, which is why it sits upstream of the architecture. It owns who can access what; what a tier costs belongs to the commercial monetization area.

## Depth by profile
| Profile | What the interview captures |
|---|---|
| `lite` | not a separate area. |
| `standard`, `regulated` | only for a product with tiers or plans: tier × capability × over-limit behaviour, plus billing-state degradation where the product bills. |

A product with one access level for everyone has no entitlement model. Write `entitlements.md` as one line, `N/A — <why>`, and stop; the line shows the readiness gate that the area was considered.

## Method
Derive the grid, then ask for the policy. The candidate tier × capability grid comes from the functional features (each `UC-` is a gatable capability) and any plan matrix the user provides. The business holds the rest: which capabilities are gated, the tiers, the limits, and the over-limit and billing-state behaviour. Offer a default for each call (gate the premium capability, soft-cap the limit) for the user to ratify.

## Rules
- A tier is defined by capability, not by price. It is an abstract access level (Free · Pro · Enterprise) whose meaning is the capabilities and limits it grants. Prices live in the monetization area and reference these tiers, which keeps entitlements upstream of pricing.
- Every entitlement names five things: the capability it gates (by `UC-` or feature id), the tier or tiers that grant it, the limit or quota (or "unlimited"), the over-limit behaviour (block · soft-cap · grace-then-block), and the enforcement boundary (where the check lives). With those it can be implemented as authorization.
- An entitlement is an access grant. Code consumes it like a permission, so it plugs into the security authorization model; roles and permissions stay defined in the security area.
- Billing-state degradation says how access changes on lapse, dunning, grace and cancellation: which capabilities are retained (read-only, data export), which are revoked, and the grace window. An unpaid account then has a specified access surface.
- Every capability has a decision. Gated capabilities are rows; the capabilities that are always-on for every tier are stated once. A feature with neither is a gap.
- State each deny, over-limit and lapsed-billing behaviour concretely enough to test, because the task that builds the gate exercises those paths.

## Output
**IDs:** `ENTL-` an entitlement (a gated capability, its tier grant and its limit).
Written under `requirements/entitlements/`:

| File | Captures | Format |
|---|---|---|
| `entitlements.md` | the tier × capability grid and the billing-state degradation | table keyed on `ENTL-`: capability (`UC-` ref) · granting tier(s) · limit/quota · over-limit · enforced-at · on-lapse; then the billing states in order |

ADRs → `adr/ADR-ENTL-NNN.md`
Consumes: the functional spec (the `UC-` capabilities to gate), the domain (capabilities and actors), and the security authorization model (the mechanism entitlements plug into). The architecture reads this area to build feature gating, quota enforcement and billing-state access.

## Excludes
pricing · plans-as-revenue · unit economics · the billing model (→ the commercial monetization area, which reads these tiers and attaches prices) · the role/permission authorization model (→ security) · billing-integration mechanics such as payment-provider wiring and invoicing (→ the solution) · the go-to-market motion (→ product vision)

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
