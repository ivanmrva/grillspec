# derive-infra-ops — worked example

Illustrative: it shows the shape, not required content.

Upstream: 99.9% availability and RTO 15 min / RPO 5 min for the booking store (`NFR-012`, `dr-tier: warm-standby`); EU-only data residency; delivery mode `trunk`.

## Decision mode (`standard`)

`topology.md`:

| Environment | Purpose | Promotes to |
|---|---|---|
| staging | release candidate; smoke and e2e target | prod (human go/no-go) |
| prod | customers | — |

Platform: AWS, `eu-west-1` for every data class (GDPR: EU-only). The environment set is parked as a ratify-point.

| Store | DR tier | Backup |
|---|---|---|
| booking store | warm-standby in `eu-central-1` (from NFR-012) | continuous, 5-min RPO |

`environments.md`:

| Key | Purpose | Secret | staging | prod |
|---|---|---|---|---|
| `DATABASE_URL` | booking store | yes | platform secret store | platform secret store, distinct |
| `PAYMENTS_API_KEY` | payment provider | yes | sandbox key | live key, vaulted |

`prerequisites.md` — names and locations, not values or console steps:

| Dependency | Where set | Config key(s) | Phase | Owner | Constraint |
|---|---|---|---|---|---|
| Payments API key | platform secret store | `PAYMENTS_API_KEY` | initial | sys-admin | PCI: live key distinct per env |
| DNS `api.example.com` | registrar | — | pre-launch | sys-admin | — |

`cicd.md`, delivery mode `trunk`:
- verification: local, the one gate before a push
- push to `main`: build → deploy to staging → smoke; a red smoke rolls back
- staging → prod: human go/no-go, rolling release
- gate, integration and scan jobs: dispatch-only

Under `pr` the same file puts the full gate on the pull request and deploys on merge, usually with a per-pull-request preview environment ahead of staging.

## Full mode (`regulated`) adds

`scaling-dr.md`: the Aurora cross-region replica (5-min lag = RPO; promote and DNS cutover within 15 min = RTO), failover-runbook owner Platform on-call, quarterly DR drill. `delivery-metrics.md`, `cost.md` and `iac.md` follow the same pattern: one decision per row, with its target or mechanism.
