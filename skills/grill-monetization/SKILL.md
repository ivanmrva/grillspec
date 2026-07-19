---
name: grill-monetization
description: >-
  Pin the business model & pricing — model, packaging, plans/tiers priced against the entitlement tiers, billing model, unit economics, and the customer-facing SLA/support commitments. Use when the entitlement tiers exist and you need the commercial model nailed down. Loads the shared grill engine.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-monetization

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Business model & pricing** — how it makes money and what each plan grants.

## Method
- Pass the **value metric** through a selection screen — value-alignment · simplicity · measurability · predictability · expansion — and pick the axis (per seat · usage · outcome, or a **hybrid** of them) that scores best; when a usage axis is chosen, **define the metering/credit unit**.
- Establish a **price-discovery basis** (willingness-to-pay): an acceptable-price corridor + a demand/elasticity curve. A competitor benchmark is only one input, not the basis.
- Treat **hybrid** as first-class — base + metered/credits + optional outcome component — not a fallback.

## Rules
- **GATED on the entitlement tiers existing** — the tiers (and what each unlocks) are defined in the **entitlements** area; without them there is nothing to price, so surface that gap rather than inventing tiers here
- each plan **attaches a price to an entitlement tier** (`ENTL-`, from the entitlements area), never to aspirational or self-invented features
- every tier price cites a **discovery basis** (corridor / elasticity point) or is marked an **`Untested`** bet — a competitor benchmark alone is not a basis. **Prices, the value-metric axis, the tier→plan packaging, and any customer-facing SLA are owner ratify-points, not skill picks:** propose a recommended price corridor / axis / SLA (concrete number + one-line why) for the owner to agree/override — `Untested` is a confidence tag, NOT a substitute for ratification. A customer-facing SLA flows to the availability NFRs **only once ratified**.
- the chosen **value metric** must pass the selection screen (value-alignment · simplicity · measurability · predictability · expansion); record why it beat the alternatives
- under usage/outcome pricing, each priced unit carries a **per-unit COGS / gross-margin-per-unit** and a **markup floor** below which the unit is never sold
- a **customer-facing SLA** (uptime / support response) is a commitment the architecture & ops must honour — record it here so it flows to the availability NFRs

## Output
Written under `commercial/monetization/`:

| File | Captures | Format |
|---|---|---|
| `business-model.md` | the business model (1 line) + packaging + the value metric (with its selection-screen scoring) + pricing axis (per seat · usage · hybrid · outcome) + metering/credit unit when usage-based | 1 line · typed fields |
| `pricing.md` | plans/tiers table — each plan **prices an entitlement tier** (`ENTL-` ref) + **target persona** + price-discovery basis + competitor benchmark | plan · price · ENTL- tier · persona · basis · billing |
| `unit-economics.md` | unit economics — LTV:CAC · CAC-payback · NRR · GRR · gross-margin · Rule-of-40 (+ per-unit COGS / markup floor under usage/outcome) | typed fields |
| `commitments.md` | customer-facing commitments per plan — **SLA** (uptime · support-response · service credits) · **support tier** · the published terms that bind the build. **Each ratified SLA commitment cites the `NFR-` id that carries it** (the flow to the quality NFRs is an ID reference, not prose — the typed-scalar agreement check then guards the value against drift; a commitment with no `NFR-` ref is a promise the build never receives) | plan · SLA · `NFR-` ref · support-tier · terms |

ADRs → `adr/ADR-MON-NNN.md`
Consumes: the **entitlement tiers** (`ENTL-`, from the entitlements area) to attach prices to + the **go-to-market motion** (billing model follows PLG vs sales-led — the motion lives in the product vision) + the **retention/churn target from goals** (it sets LTV's denominator — sourced upstream, not from post-launch growth). The competitor price benchmark is **elicited** here as price-discovery input, not read from an upstream artifact.

## Excludes
the **entitlement model itself** — tiers · feature gating · limits · billing-state access (→ the **entitlements** area; this area only attaches *prices* to its tiers) · the *domain mechanics* of subscriptions (→ the domain model) · billing implementation (→ the architecture)

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
