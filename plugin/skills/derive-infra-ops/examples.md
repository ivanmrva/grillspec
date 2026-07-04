# derive-infra-ops — worked example

From the NFRs: *"99.9% availability, RTO 15 min / RPO 5 min for the booking store; EU-only data residency; serverless-leaning stack."* That recorded input drives the deploy & operations architecture below.

**Topology** (`topology.md`) — three env tiers, EU-pinned, segmented:
```mermaid
flowchart LR
  subgraph public[Public zone]
    WAF[WAF + ALB]
  end
  subgraph private[Private zone · eu-west-1]
    API[Booking API · Fargate] --> DB[(Aurora PG · Multi-AZ)]
    API --> Q[SQS jobs]
  end
  WAF --> API
  Q -. controlled egress .-> EXT[Payments]
```
dev / stage / prod are the same module, region-pinned `eu-west-1`; config-in-environment, immutable artifacts.

**IaC** (`iac.md`): Terraform; one module reused across dev/stage/prod with per-env tfvars; remote state in an S3 backend with state locking — no console drift.

**CI/CD stage** (`cicd.md`) — on merge to `main`:
> deploy app → **dev environment** → run e2e/integration pipeline → **canary** release (10% → 100%). Promotion signal: error-budget burn-rate < 2× over the 1h window; abort/rollback if exceeded. Feature flags decouple deploy from release.
> (on-MR: build · full test suite · conformance · gates incl. **SLSA** provenance/signing — green before merge.)

**Delivery-metric target** (`delivery-metrics.md`):

| metric | target | instrumentation |
|---|---|---|
| change-failure rate | < 15% | deploy events ⨯ incident tags in the pipeline ledger |

*(deployment frequency · change lead time · failed-deployment recovery time are set + instrumented the same way.)*

**DR tier** (`scaling-dr.md`) — for the RTO 15 / RPO 5 booking store:
> **warm-standby** in `eu-central-1` (Aurora cross-region replica, 5-min lag = RPO; promote + DNS cutover ≤ 15 min = RTO). Failover-runbook owner: **Platform on-call**. Day-2: quarterly DR drill + test-restore.

**Cost practice** (`cost.md`): allocate by tag `team`+`env`+`tenant`; unit-cost = **$ / 1k bookings**; levers = Fargate right-sizing · 1-yr Savings Plans · Spot for async workers; anomaly alert > 20% WoW; monthly per-tenant showback; `eu-west-1` chosen partly on carbon intensity.

**Human-only prerequisites** (`prerequisites.md`) — the **requirement register**: one row per dependency, **names + locations + config keys, never values, no console click-path** (those are `bootstrap.md`, downstream):

| dependency | where set | config key(s) | phase | owner | residency/compliance |
|---|---|---|---|---|---|
| AWS account + billing alarm + quotas (Fargate vCPU · Aurora ACUs) | AWS org console | — | initial | ops-admin | — |
| Payments API key | CI + platform secret store | `PAYMENTS_API_KEY` | initial | sys-admin | PCI: prod key vaulted, distinct per env |
| DB master credential | IaC backend | `DB_MASTER` | initial | sys-admin | — |
| SSO OAuth/app registration | IdP console | `OIDC_CLIENT_ID`/`_SECRET` | pre-launch | ops-admin | — |
| DNS `api.example.com` | registrar/Route 53 | — | pre-launch | sys-admin | — |
| Residency region `eu-west-1` | AWS account | (region pin) | initial | ops-admin | GDPR: EU-only |

Recorded: each availability/RTO/RPO NFR → a mechanism + DR tier; flags decouple deploy from release; the rollout names a burn-rate promotion/abort signal; cost as a *practice*, not a number; the human prerequisites captured as a register (WHAT + who + which key) — the click-by-click to provision each lives in the walking-skeleton's `12-operate/bootstrap.md`, which references this register upstream.
