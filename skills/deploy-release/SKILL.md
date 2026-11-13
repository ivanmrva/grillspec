---
name: deploy-release
description: >-
  Promote a built increment along the project's promotion path — preflight, deploy through the pipeline, smoke-check, watch, roll back on breach — and prepare the production go/no-go for the human. Use when landed work needs to reach an environment. Loads the shared exec engine.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# deploy-release

**Load `references/exec-engine.md` first and follow it.** This skill moves a built increment through real environments and confirms it is running there. It operates the pipeline the project already has; it changes no code and no spec.

## How a deploy happens
The promotion path — which environments exist, their order, and the gate at each hop — is the project's ratified decision, in `09-solution/infra-ops/topology.md` and `cicd.md` (on a `lite` project, in the solution strategy and the conventions). Follow it as written.

The first hop follows the project's `delivery` setting (the engine's Delivery table): under `trunk` a push to the default branch deploys and is smoke-checked; under `pr` the merge of a green pull request does. Either way the smoke check against the deployed environment is the signal that it shipped.

Later hops follow the gates in `cicd.md`. A hop marked automatic proceeds when its gate is green. Promotion to production is the human's decision: prepare the evidence, state your recommendation, and wait for an explicit go — unless the owner has ratified an auto-promote policy for that hop. The default to propose is automatic promotion between pre-production environments and a human go for production.

## Process
1. **Identify the increment and the target.** The commit or version, the tasks it contains, and the target environment on the promotion path. Where the pipeline has a provenance or signing gate (a `regulated` project's pipeline hardening), confirm the artifact's attestation matches before promoting it.
2. **Run `preflight` in the target before it takes traffic.** Required configuration present, dependencies reachable and authenticating, migrations applied, the readiness endpoint green. A red preflight stops the promotion: the environment is not what the artifact needs.
3. **Deploy through the pipeline.** The pipeline is the description of how the system gets deployed; a hand-applied change leaves the environment in a state nothing describes and the next deploy may undo. `check_deploy_real.py` is the static check that the pipeline really deploys.
4. **Check and watch.** Run the smoke checks, then watch the objectives and alerts the change could affect (`SLO-`) through the rollout. On a breach, roll back by the procedure `cicd.md` defines and report what happened.
5. **Where the rollout is progressive, let the metric gate decide.** A canary is promoted or aborted by the queries and thresholds the pipeline names, not by a reading of a dashboard. Feature flags keep deploy and release separate: ship dark, enable as its own step.
6. **Record what a later reader needs** (Output).

An environment that cannot be reached — an account not provisioned, a missing credential or DNS record — is a blocker to escalate through `spec/_human-input.md`, with the provisioning steps in `12-operate/bootstrap.md`. Report the deploy as not run; a deploy that did not happen is never described as done.

## Before the first production promotion: the readiness review
The first promotion to production passes a production-readiness review. It mostly points at evidence that already exists and adds one bar: verified, not only planned. Include the items the product actually has:

| Item | Verified means |
|---|---|
| system-suite results | the latest run's measured results against their bars (from the system-suite run), for this increment |
| security | no open blocking finding against a `SEC-` rule |
| rollback | rehearsed in a pre-production environment, not only designed |
| backups and recovery | a test restore was run; the recovery mechanism was exercised to its tier |
| observability | objectives and alerts are receiving data in production |
| configuration | `preflight` green, and `check_config_drift.py` clean (the configuration matrix matches what the code reads) |
| cost | guardrails and anomaly alerts are on, where the project set them |
| operations | the day-2 steps exist in `bootstrap.md` |

An unverified item blocks go-live and is put to the human with the go/no-go; it is not shipped silently. In pre-production environments the same list is advisory: ship freely there and report an unmet item as a known risk.

In any environment, do not promote without a rollback path, with the smoke checks failing, or — where the project defines objectives — before their alerts exist.

## A new environment: extend the setup runbook
Promoting to an environment for the first time, production above all, fills in phases B and C of `12-operate/bootstrap.md` (the walking skeleton wrote phase A). Compose the prerequisites register and the configuration matrix (`infra-ops/prerequisites.md`, `environments.md`) into steps an operator can follow in the current consoles without guessing: this environment's distinct configuration keys, the production-only prerequisites (DNS, certificates, scale and residency, production credentials), the go-live checklist, and the day-2 steps (rotation, scaling, another environment). The register says what must exist and who owns it; the runbook is the only place that says how. It states where each value is set and never the value.

## Output
Written under `12-operate/`. These are dated operations records; write one when someone will read it, and keep it to what they need.

| File | When | Captures |
|---|---|---|
| `deploy-<env>-<version>.md` | a production promotion, and any deploy that failed or was rolled back. Routine pre-production deploys are recorded by the pipeline's own history. | what was deployed · environment · version · the tasks it contains · rollout strategy and gate result · who gave the go · outcome. On a `regulated` project also provenance, and `change-failed` · `intervention` · `recovery-time`, which feed its delivery metrics. |
| `production-readiness.md` | the first production promotion | the review above: item · evidence · verified? · and the go/no-go |
| `bootstrap.md` (extend) | a new environment | phases B and C of the setup runbook |
| `adr/ADR-REL-NNN.md` | a costly-to-reverse release decision | ADR |

Reads: the landed increment, the promotion path and rollback procedure, the objectives and alerts, and the latest system-suite results.

## Resources
- `references/exec-engine.md`
- Worked example: `examples.md`
