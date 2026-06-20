---
name: derive-infra-ops
description: >-
  Design topology, IaC, CI/CD, deploy/release strategy, environments, scaling/HA, DR/BCP, backup/restore, capacity and cost from the NFRs and constraints. Use when the NFRs and constraints exist and you need the deploy & operations architecture designed. Loads the shared derive engine.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-infra-ops

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **Infrastructure, deploy & operations** — the application's deployment & operations architecture.

## Method
1. per availability/RTO/RPO NFR: a mechanism + its **DR tier** (backup-restore / pilot-light / warm-standby / active-active) with a named failover-runbook owner
2. topology → environments (dev/stage/prod) → IaC
3. CI/CD → progressive-delivery strategy: **feature flags** decouple deploy from release; each rollout strategy names its **promotion/abort signal** (tied to an observability burn-rate) + rollback
4. set the **delivery-metric targets** the pipeline must hit + how each is instrumented (deployment frequency · change lead time · change-failure rate · failed-deployment recovery time)
5. backup/DR → the **cost practice** (allocation/tagging · unit-cost · optimization levers · anomaly alerting + showback) incl. a carbon/efficiency line
6. the day-2 operations plan (drills/patching/capacity/cost cadence)

## Rules
- governing principles: **config-in-environment** (config from env, not baked into the artifact) + **immutable-infrastructure** (replace, never mutate, running instances)
- every availability/RTO/RPO NFR has a mechanism; each names a **DR tier** (backup-restore / pilot-light / warm-standby / active-active) per its RTO/RPO class + a failover-runbook owner; environments + progressive-delivery strategy defined; backup/restore + DR specified; cost modelled
- **progressive delivery**: **feature flags** decouple deploy from release; each rollout strategy (blue-green/canary/rolling) names its **promotion/abort signal** tied to an observability burn-rate + rollback
- **delivery-metric targets** are set and instrumented: deployment frequency · change lead time · change-failure rate · failed-deployment recovery time
- **CI/CD is GitHub Actions** (`.github/workflows/`): **on MR** → build · full test suite · full conformance · gate checks incl. a **build-provenance/signing gate** (emit **SLSA** provenance) (green before merge); **on merge to `main`** → deploy the app to the **dev environment** then run the e2e/integration pipeline. The release/rollout step consumes the chosen **rollout strategy** (blue-green/canary/rolling + rollback). The hosted Claude Code Review App is deliberately NOT wired in — run `/code-review` ad hoc
- **continuous-ops (day-2) plan present** as *planned operational requirements* (not concrete prod tasks): DR-drill / test-restore cadence · patching/dependency-refresh cadence · capacity re-planning (the growth→infra loop) · cost-review cadence
- **human-only prerequisites enumerated** as a first-class list (names + locations, **never values**): accounts + billing/quotas · secret/credential names + where each is set (CI · platform · IaC backend) · OAuth/app registrations · DNS records · account-gated region/residency choices — consumed by the walking-skeleton to front-load the bootstrap
- network carries **security zones/segmentation** (ingress WAF/LB · controlled egress · private/public); data-residency region pinned at infra per class
- **the cloud provider + residency region are ratify-points, not merit picks** — both are org commitments / one-way doors (existing accounts · vendor contracts · residency law); take them from the constraints, and where the constraints are silent **ratify a default — never silently assume one**
- scope boundary: telemetry/SLOs/alerting/runbooks → the observability area; coding rules + code hooks → the conventions area; **`spec/`+docs governance (`lint_spec.py`, the generated doc-site) is a separate framework-level concern, NOT this pipeline**

## Output
Written under `solution/infra-ops/`:

| File | Captures | Format |
|---|---|---|
| `topology.md` | deployment topology in Mermaid (compute · network with security zones/segmentation · stores) + environments (dev/stage/prod) | Mermaid |
| `iac.md` | infrastructure-as-code approach | typed: IaC approach |
| `cicd.md` | the app's CI/CD pipeline (GitHub Actions) stages: on-MR (build · tests · conformance · gates incl. SLSA provenance/signing) · on-merge-to-main (deploy dev → e2e/integration) · progressive delivery (flags decouple deploy/release; rollout promotion/abort signal ⇄ burn-rate) | typed: CI/CD stages |
| `delivery-metrics.md` | delivery-metric targets + instrumentation: deployment frequency · change lead time · change-failure rate · failed-deployment recovery time | typed: metric · target · instrumentation |
| `scaling-dr.md` | scaling/HA + backup/restore + DR/BCP (RTO/RPO mechanism + DR tier per class + failover-runbook owner) + day-2 cadences (DR drills · patching · capacity re-planning) | typed: scaling rule · RTO/RPO mechanism · DR tier |
| `cost.md` | cost *practice*: allocation/tagging model · unit-cost (e.g. per-tenant) · optimization levers (right-sizing/commitments/spot) · anomaly alerting + showback · carbon/efficiency (region carbon intensity, right-sizing as a lever) | typed: cost practice · line items |
| `prerequisites.md` | the human-only bootstrap prerequisites — accounts/billing/quotas · secret/credential names + where set · OAuth/app regs · DNS · region/residency choices (names + locations, never values) | prose |

ADRs → `adr/ADR-INFRA-NNN.md`
*(DERIVED & regenerate-only — never hand-edited)*
Consumes: the quality NFRs (availability/RTO/RPO, scale) + the constraints (residency, vendor commitments, budget) + the architecture's deployable units.

## Excludes
implementation code · SLO/alerting/runbook detail (→ the observability area)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
