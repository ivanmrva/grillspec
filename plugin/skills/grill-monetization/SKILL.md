---
name: grill-monetization
description: >-
  Pin prices and plans: the business model in a line, the value metric, and each plan priced
  against an entitlement tier with the basis for its price. An optional commercial area; use only
  when the user asks for pricing work.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-monetization

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Business model & pricing** — how it makes money and what each plan grants.

Run this only when the user asks for it; nothing in the build path depends on it. The tiers the code enforces live in the entitlements area, and the availability the build delivers lives in the quality requirements.

## Depth by profile
Optional at every profile. Capture what the user will use:

- By default, prices and plans: `pricing.md`, plus the one-line model and the value metric in `business-model.md`.
- `unit-economics.md`, when the user is building a financial case.
- `commitments.md`, when the product publishes an SLA or support terms.

## Rules
- Choose the value metric (per seat · usage · outcome, or a hybrid) by judging it against five criteria: value alignment · simplicity · measurability · predictability · expansion. Record in a sentence why it beat the alternatives. A hybrid (a base plus metered units or credits, with an optional outcome component) is a first-class choice. A usage axis needs its metering or credit unit defined.
- Price from willingness-to-pay evidence: an acceptable-price corridor and a demand or elasticity curve. A competitor benchmark is one input to that basis.
- Each plan prices an entitlement tier (`ENTL-`) from the entitlements area. A single-plan product says in a line what the plan includes. When the product has several plans and no entitlements area, raise that gap; tiers invented here would be a second source the code does not enforce.
- Every price cites its discovery basis, or is marked an `Untested` bet. `Untested` is a confidence tag and does not replace ratification: prices, the value metric, the packaging and any customer-facing SLA are the owner's to ratify.
- Under usage or outcome pricing, each priced unit carries its per-unit cost and a markup floor below which it is not sold.
- A customer-facing SLA is published against an `NFR-` the quality area carries, and cites its id. A plan that needs a stronger number raises it with the quality area first, because a commitment the quality requirements do not hold is a promise the build never receives.

## Output
Written under `commercial/monetization/`:

| File | Captures | Format |
|---|---|---|
| `business-model.md` | the business model in one line · packaging · the value metric and why it was chosen · the pricing axis · the metering or credit unit when usage-based | 1 line + typed fields |
| `pricing.md` | the plans, each pricing an entitlement tier | plan · price · `ENTL-` tier · persona · basis · billing |
| `unit-economics.md` | LTV:CAC · CAC payback · NRR · GRR · gross margin · Rule of 40; per-unit cost and markup floor under usage or outcome pricing | typed fields |
| `commitments.md` | customer-facing commitments per plan: SLA (uptime · support response · service credits) · support tier · published terms | plan · SLA · `NFR-` ref · support-tier · terms |

ADRs → `adr/ADR-MON-NNN.md`
Consumes: the entitlement tiers (`ENTL-`) to attach prices to, the go-to-market motion from the product vision (the billing model follows self-serve or sales-led), and the retention target from the goals (it sets the denominator of LTV). The competitor benchmark is elicited here.

## Excludes
the entitlement model itself — tiers · feature gating · limits · billing-state access (→ the entitlements area; this area only attaches prices to its tiers) · the domain mechanics of subscriptions (→ the domain model) · billing implementation (→ the architecture)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
