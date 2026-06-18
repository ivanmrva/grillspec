# grill-entitlements — worked example

> **User:** Three plans — Free, Pro, Enterprise. Pro is the paid default.

> **Claude:** I derived the gatable capabilities from the functional spec (`UC-`) and built the tier×capability grid — **tiers by capability, not price** (the price lives in the commercial monetization area and references these tiers). I gated the premium capabilities, set limits with an explicit over-limit behaviour, named the enforcement boundary for each, and specified how access degrades when billing lapses. Two calls I ratified with you (default in brackets); the rest derived.

**`entitlements.md`** (excerpt):

| ENTL- | Capability (UC-) | Granting tier(s) | Limit / quota | Over-limit | Enforced at | On lapse |
|---|---|---|---|---|---|---|
| ENTL-001 | Create project (UC-012) | Free+ | 3 (Free) · ∞ (Pro+) | block + upsell | application service | retain (read-only) |
| ENTL-002 | Invite member (UC-031) | Pro+ | 25 (Pro) · ∞ (Ent) | soft-cap + notify | application service | revoke new invites |
| ENTL-003 | SSO / SCIM (UC-044) | Enterprise | — | — | gateway (auth) | retain (security) |
| ENTL-004 | API access (UC-050) | Pro+ | 10k req/day (Pro) | grace-then-block | gateway (rate) | revoke after grace |

**Billing-state degradation** (specified, not improvised): `active → grace (14d, full access) → dunning (read-only + export) → lapsed (Free entitlements only; data retained 90d) → cancelled (export-only 30d)`.

Notes:
- `ENTL-003` plugs into the **security** authz model (SSO is an auth mechanism); entitlements grant it, security defines it.
- The **monetization** area reads this grid to attach prices to `Free/Pro/Enterprise` — it never feeds back, so entitlements stay upstream of pricing and of the architecture gate.
- `UC-061` (export data) was un-gated on review → recorded as **always-on** (a legal data-rights obligation), not left as a silent default.
