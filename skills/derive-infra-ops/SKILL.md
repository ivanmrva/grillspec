---
name: derive-infra-ops
description: >-
  Decide how the system is deployed and operated — environments and promotion path, DR tier, the config matrix, external prerequisites, the CI/CD pipeline; at the regulated profile also IaC, delivery metrics, scaling/DR and cost. Use when the NFRs and constraints exist.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# derive-infra-ops

**Load `references/derive-engine.md` first and follow it.** This skill applies that method to **infrastructure, deploy & operations**: where the system runs, how a change reaches production, and what must exist before it can.

## Depth by profile
How much is written follows the project's profile:

| Profile | Mode | Written |
|---|---|---|
| `lite` | N/A | nothing here — the environments and promotion path are a row in `arch/solution-strategy.md`, the pipeline and config rules are in the conventions |
| `standard` | decision mode | `topology.md`, `environments.md`, `prerequisites.md`, `cicd.md` |
| `regulated` | full mode | those four plus `iac.md`, `delivery-metrics.md`, `scaling-dr.md`, `cost.md` |

Decisions live in the spec; the description lives in the artifact that enforces it — here the workflow files and the infrastructure code — and once they exist they are the source of truth for pipeline and infrastructure detail. Decision mode therefore records only the environments and how a change is promoted through them, the DR and backup tier, the configuration each environment needs, and what a human has to provision; full mode also writes the operations design, because at `regulated` it is a deliverable other teams and auditors read.

## Decision record

### `topology.md`
- **The environment set and promotion path.** Each environment with its purpose, and the order a change moves through them. This is a ratify-point: team schemes vary (no stage, several production regions, a UAT tier, ephemeral-only) and the spec cannot derive them. Propose a default that fits the product, for example `dev · stage · prod` plus per-change preview environments for a web product, and surface it as the engine describes.
- **The hosting platform and residency region.** Both are organisation commitments (existing accounts, vendor contracts, residency law). Take them from the constraints; where the constraints are silent, surface a default as a ratify-point. The region is pinned per data class.
- **The DR and backup tier per store.** It realises the `dr-tier` ratified on the availability/RTO/RPO NFR. A tier that NFR left blank is a gap to record against the NFR, not a pick to make here.

### `environments.md`
The environment × configuration matrix: every config key, env var and secret the system needs, with its purpose, whether it is a secret, and per environment its value source, where it is stored or injected and its owner. It shows which environments share a key and which hold a distinct one (for example preview ≡ staging on most keys, production distinct), and the per-environment platform settings (region · scale · flags). The key is the leading column, with one column per environment, because the build reconciles the keys the code reads against this matrix.

### `prerequisites.md`
The register of external dependencies a human must provision, one row each: name · where it is set (CI · platform · IaC backend) · the config key(s) it feeds (→ `environments.md`) · phase · owner · any residency or compliance constraint · how the value travels (captured from → stored in → set per environment).
- Coverage: accounts with their billing and quotas · secret and credential names · OAuth/app registrations · DNS records · account-gated region choices.
- Phase: `initial` (bring up local and dev) · `pre-launch` (production, before go-live) · `later` (rotation, scale, new regions).
- Owner: `ops-admin` (accounts, billing, org policy) · `sys-admin` (DNS, network, secrets store, IaC backend) · `developer` (local env, app config).

The register states what must exist and who owns it. It holds names and locations only: a secret's value is not written into the spec, and the click-by-click provisioning steps belong to the operate-layer runbook `12-operate/bootstrap.md`, which references this register.

### `cicd.md`
The pipeline is GitHub Actions (`.github/workflows/`). Keep the file short: the stages, the gate at each, and the promotion workflow. It describes the pipeline for the project's delivery mode — the `delivery` setting reported with the profile, `pr` when unset:

| | `trunk` | `pr` |
|---|---|---|
| Verification | local — the project's one gate, run before a push | the same local gate, then the full gate on the pull request; merge on green |
| Deploy | CI deploys the default branch to the first environment of the promotion path, then smokes it | on merge, CI deploys to the first environment of the promotion path, then runs the e2e/integration pipeline |
| Other jobs (gate, integration, scans) | defined, dispatch-only | part of the pull-request gate |

In both delivery modes `cicd.md` defines the end-to-end promotion workflow: the ordered hops across the ratified environments through to production and the gate at each hop (automatic, or a human go/no-go), with the rollout strategy (blue-green · canary · rolling) and its rollback. The build wires this workflow as written, so nothing about it is left to re-derive. An AI code-review integration is not part of the pipeline; review runs through the agent host's own review workflow when wanted.

## Rules
Config comes from the environment and is not baked into the artifact, and a running instance is replaced, not mutated. One artifact then promotes unchanged through every environment.

## Full mode
At `regulated` the skill also decides and records the items below. In decision mode they are not raised.
- **Deployment diagram** (in `topology.md`): compute · the network with its security zones (ingress WAF/load balancer · controlled egress · private/public) · stores.
- **IaC** (`iac.md`): the infrastructure-as-code approach.
- **Pipeline hardening** (in `cicd.md`): a build-provenance and signing gate (SLSA provenance), and progressive delivery — feature flags decouple deploy from release, and each rollout strategy names its promotion/abort signal, tied to an observability burn rate.
- **Delivery metrics** (`delivery-metrics.md`): a target and its instrumentation for deployment frequency · change lead time · change-failure rate · failed-deployment recovery time. The targets are organisation commitments, so each is a ratify-point.
- **Scaling and DR** (`scaling-dr.md`): scaling/HA rules · backup and restore · the RTO/RPO mechanism that realises each DR tier, with a named failover-runbook owner · the day-2 cadences (DR drill and test restore, patching and dependency refresh, capacity re-planning). These are planned operational requirements, not concrete production tasks.
- **Cost** (`cost.md`): the cost practice — allocation/tagging model · unit cost (for example per tenant) · optimisation levers (right-sizing, commitments, spot) · anomaly alerting and showback · the review cadence · a carbon/efficiency line.

## Output
Written under `solution/infra-ops/`:

| File | Mode | Captures | Format |
|---|---|---|---|
| `topology.md` | decision | the decision record above | table: environment · purpose · promotes to; table: store · DR tier · backup. Full mode adds a Mermaid diagram |
| `environments.md` | decision | the decision record above | matrix: key is the leading column · one column per environment |
| `prerequisites.md` | decision | the decision record above | table, one row per dependency, keyed by its name |
| `cicd.md` | decision | the decision record above | typed: stages · gates · ordered hops |
| `iac.md` | full | the IaC approach | typed fields |
| `delivery-metrics.md` | full | delivery-metric targets and instrumentation | table: metric · target · instrumentation |
| `scaling-dr.md` | full | scaling/HA · backup/restore · DR mechanism · day-2 cadences | typed: scaling rule · RTO/RPO mechanism · DR tier · owner |
| `cost.md` | full | the cost practice | typed: practice · line items |

ADRs → `adr/ADR-INFRA-NNN.md`
Consumes: the quality NFRs (availability/RTO/RPO, scale) · the constraints (residency, vendor commitments, budget) · the architecture's deployable units.

## Excludes
implementation code · SLO/alerting/runbook detail (→ the observability area) · coding rules and code hooks (→ the conventions area) · governance of the spec and docs (the spec linter and the doc site are a separate concern from this pipeline)

## Resources
- `references/derive-engine.md`
- Worked example: `examples.md`
