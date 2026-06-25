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
2. topology → environments (dev/stage/prod) → IaC → **the environment×configuration matrix**: every config key / env-var / secret the system needs, its per-environment value-source + where-stored/injected + owner, and the **cross-environment mapping** (which environments share a key vs. hold a distinct one — e.g. preview≡staging on most keys, prod distinct)
3. CI/CD → progressive-delivery strategy: **feature flags** decouple deploy from release; each rollout strategy names its **promotion/abort signal** (tied to an observability burn-rate) + rollback
4. set the **delivery-metric targets** the pipeline must hit + how each is instrumented (deployment frequency · change lead time · change-failure rate · failed-deployment recovery time)
5. backup/DR → the **cost practice** (allocation/tagging · unit-cost · optimization levers · anomaly alerting + showback) incl. a carbon/efficiency line
6. the day-2 operations plan (drills/patching/capacity/cost cadence)

## Rules
- governing principles: **config-in-environment** (config from env, not baked into the artifact) + **immutable-infrastructure** (replace, never mutate, running instances)
- every availability/RTO/RPO NFR has a mechanism; each names a **DR tier** (backup-restore / pilot-light / warm-standby / active-active) per its RTO/RPO class + a failover-runbook owner; environments + progressive-delivery strategy defined; backup/restore + DR specified; cost modelled
- **progressive delivery**: **feature flags** decouple deploy from release; each rollout strategy (blue-green/canary/rolling) names its **promotion/abort signal** tied to an observability burn-rate + rollback
- **delivery-metric targets** are set and instrumented: deployment frequency · change lead time · change-failure rate · failed-deployment recovery time
- **CI/CD is GitHub Actions** (`.github/workflows/`): **on MR** → build · full test suite · full conformance · gate checks incl. a **build-provenance/signing gate** (emit **SLSA** provenance) (green before merge); **on merge to `main`** → deploy the app to the **first environment of the ratified promotion path** (the path's leading env — `dev`, or a dynamic per-PR preview env, per the ratified environment set) then run the e2e/integration pipeline. **Define the END-TO-END promotion workflow explicitly** — the ordered hops across the ratified environments and the **gate at each hop** (auto-promote vs. human go/no-go, tied to the rollout strategy's promotion/abort signal), through to prod — so the build skills wire it rather than re-deriving it. The release/rollout step consumes the chosen **rollout strategy** (blue-green/canary/rolling + rollback). The hosted Claude Code Review App is deliberately NOT wired in — run `/code-review` ad hoc
- **continuous-ops (day-2) plan present** as *planned operational requirements* (not concrete prod tasks): DR-drill / test-restore cadence · patching/dependency-refresh cadence · capacity re-planning (the growth→infra loop) · cost-review cadence
- **human-only prerequisites enumerated** as a first-class list — **per item: the name + where it's set + the exact step-by-step actions to provision it and where to inject it, but NEVER the value itself** (a secret's value is never written to the spec): accounts + billing/quotas · secret/credential names + where each is set (CI · platform · IaC backend) · OAuth/app registrations · DNS records · account-gated region/residency choices — actionable enough that a non-expert can execute each without guessing; consumed by the walking-skeleton to front-load the bootstrap
- **the prerequisites guide is operationally complete, not a bare list** — for **each external system / platform**, a step-by-step provisioning walkthrough that targets the platform's **current** console/UI (verify against current vendor docs — never a remembered, possibly-stale click-path), tagged two ways so an operator knows their lane and their timing: by **phase** — `initial` (needed to bring up local + dev) · `pre-launch` (production, before go-live) · `later` (day-2: rotation, scale, new regions) — and by **audience** — `ops-admin` (accounts/billing/org policy) · `sys-admin` (DNS/network/secrets store/IaC backend) · `developer` (local env, app config). State, per system, **what must be set up in advance vs. what can wait**, and what to **capture** (the value to record), **where to store it** (which secret store / CI / platform config), and **how to author it per environment**
- **the environment×configuration matrix is explicit** (`environments.md`) — the design of configuration across environments: every key's purpose · secret-or-plain · per-environment {value-source · where-stored/injected · owner} · the **cross-environment relationship** (shared vs. distinct — call out exactly which environments collapse onto the same value and which stand alone) · per-environment platform settings (region/residency · scale/size · flags). This is the source of truth the bootstrap runbook composes from; **config-in-environment** means this matrix, not values baked in code
- network carries **security zones/segmentation** (ingress WAF/LB · controlled egress · private/public); data-residency region pinned at infra per class
- **the cloud provider + residency region are ratify-points, not merit picks** — both are org commitments / one-way doors (existing accounts · vendor contracts · residency law); take them from the constraints, and where the constraints are silent **ratify a default — never silently assume one**
- **the environment set (count + purpose) + promotion path are a ratify-point, never a silent default** — propose a profiled default (e.g. `dev · stage · prod`, plus ephemeral per-PR preview envs for a web/PLG product) WITH its promotion path, then **surface it for the human to confirm or override**; org/team schemes genuinely vary (no stage · multiple prod regions · a sandbox/UAT tier · ephemeral-only) and this is a team fact the spec can't derive. Record the ratified set + each environment's purpose in `topology.md`; an un-ratified default is an assumption to flag, not a settled fact
- scope boundary: telemetry/SLOs/alerting/runbooks → the observability area; coding rules + code hooks → the conventions area; **`spec/`+docs governance (`lint_spec.py`, the generated doc-site) is a separate framework-level concern, NOT this pipeline**

## Output
Written under `solution/infra-ops/`:

| File | Captures | Format |
|---|---|---|
| `topology.md` | deployment topology in Mermaid (compute · network with security zones/segmentation · stores) + environments (dev/stage/prod) | Mermaid |
| `iac.md` | infrastructure-as-code approach | typed: IaC approach |
| `cicd.md` | the app's CI/CD pipeline (GitHub Actions) stages: on-MR (build · tests · conformance · gates incl. SLSA provenance/signing) · on-merge-to-main (deploy the **leading env of the promotion path** → e2e/integration) · the **end-to-end promotion workflow** (ordered env hops + the gate at each: auto-promote vs. human go/no-go through to prod) · progressive delivery (flags decouple deploy/release; rollout promotion/abort signal ⇄ burn-rate) | typed: CI/CD stages + promotion workflow |
| `delivery-metrics.md` | delivery-metric targets + instrumentation: deployment frequency · change lead time · change-failure rate · failed-deployment recovery time | typed: metric · target · instrumentation |
| `scaling-dr.md` | scaling/HA + backup/restore + DR/BCP (RTO/RPO mechanism + DR tier per class + failover-runbook owner) + day-2 cadences (DR drills · patching · capacity re-planning) | typed: scaling rule · RTO/RPO mechanism · DR tier |
| `cost.md` | cost *practice*: allocation/tagging model · unit-cost (e.g. per-tenant) · optimization levers (right-sizing/commitments/spot) · anomaly alerting + showback · carbon/efficiency (region carbon intensity, right-sizing as a lever) | typed: cost practice · line items |
| `environments.md` | the environment×configuration matrix: each key/env-var/secret · purpose · secret? · per-environment {value-source · where-stored/injected · owner} · cross-environment mapping (shared vs distinct) · per-environment platform settings (region/residency · scale · flags) | matrix: key is leading column · one column per environment |
| `prerequisites.md` | the per-platform provisioning guide — accounts/billing/quotas · secret/credential names + where set · OAuth/app regs · DNS · region/residency choices. **Per item: name + location + the exact current-console step-by-step + where to inject — never the value**; each tagged by **phase** (initial/pre-launch/later) and **audience** (ops-admin/sys-admin/developer), with capture→store→author-per-env called out | prose: per-platform, per-item step-by-step, grouped by phase + audience |

ADRs → `adr/ADR-INFRA-NNN.md`
*(DERIVED & regenerate-only — never hand-edited)*
Consumes: the quality NFRs (availability/RTO/RPO, scale) + the constraints (residency, vendor commitments, budget) + the architecture's deployable units.

## Excludes
implementation code · SLO/alerting/runbook detail (→ the observability area)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
