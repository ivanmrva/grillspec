# grill-entitlements — worked example

Illustrative: it shows the shape of the output, not a list to fill.

> **User:** Three plans: Free, Pro, Enterprise. Pro is the paid default.
> **Agent:** I built the grid from the use-cases. Two calls are yours: I'd cap Free at 3 projects and block with an upsell, and I'd soft-cap Pro at 25 members with a notice. Agree?
> **User:** Yes to both.
> **Agent:** When a Pro account stops paying, I'd give 14 days of full access, then read-only with export, then drop to Free.
> **User:** Fine. Keep their data for 90 days after that.

## Output — `entitlements.md`
| ENTL- | Capability (UC-) | Granting tier(s) | Limit / quota | Over-limit | Enforced at | On lapse |
|---|---|---|---|---|---|---|
| ENTL-001 | Create project (UC-012) | Free+ | 3 (Free) · ∞ (Pro+) | block + upsell | application service | retain (read-only) |
| ENTL-002 | Invite member (UC-031) | Pro+ | 25 (Pro) · ∞ (Ent) | soft-cap + notify | application service | revoke new invites |
| ENTL-003 | SSO / SCIM (UC-044) | Enterprise | — | — | gateway (auth) | retain |
| ENTL-004 | API access (UC-050) | Pro+ | 10k req/day (Pro) | grace-then-block | gateway (rate) | revoke after grace |

Always-on for every tier: data export (UC-061), a data-rights obligation, and every use-case not listed above.

Billing states: `active → grace (14 d, full access) → dunning (read-only + export) → lapsed (Free entitlements; data retained 90 d) → cancelled (export only, 30 d)`.

ENTL-003 grants SSO; the security area defines it. The tiers carry no prices: the monetization area attaches them.
