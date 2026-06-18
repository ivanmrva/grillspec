---
name: deploy-release
description: >-
  Promote a built increment through environments with an explicit rollout/rollback strategy and smoke-verify in the target. Use when a merged increment needs promoting to an environment. Loads the shared exec core.
disable-model-invocation: true
argument-hint: a built increment to deploy
---

# deploy-release

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **deploy & release to real environments**.

## Process
1. **Verify release provenance first** — check the artifact's build-provenance level / attestation digest before it enters an environment; reject an unattested or digest-mismatched artifact.
2. Promote as a **declarative, continuously-reconciled** change (desired revision → reconciler converges the environment); record the reconciled revision rather than hand-applying steps. Strategy: blue-green / canary / rolling.
3. For canary/progressive rollout, gate promotion on a **metric gate** — explicit queries · thresholds · auto-promote/abort — not a prose "healthy signals" judgment.
4. Keep deploy decoupled from release via feature flags — ship dark, enable separately.
5. Run post-deploy smoke checks and watch the relevant `SLO-`/alerts during rollout; roll back on breach per the defined procedure.
6. Never hand-deploy outside the IaC/CD path.

## Rules
- The release-readiness checklist is advisory — the system never blocks a release, but shipping with it unmet is a known risk. **Never pass on:** a missing rollback path · SLOs/alerts not in place · smoke checks failing · an artifact with no verified provenance.
- Canary verdict comes from the metric gate's thresholds, never a subjective read of the dashboards.

## Output
Written under `10-operate/`:

| File / target | Captures | Format |
|---|---|---|
| `deploy-<env>-<version>.md` | deploy record: what · env · version · provenance (level / attestation digest) · reconciled revision · rollout strategy + metric-gate verdict · **change-failed? (Y/N)** · **intervention (hotfix/rollback/forward)** · **recovery-time** · checklist outcome | — |

(the change-failed? / intervention / recovery-time fields feed a change-failure-rate + recovery-time rollup across deploys)

ADRs → `adr/ADR-REL-NNN.md`
(no spec/code changes — operates the running system)
Consumes: the merged increment + `07-solution/infra-ops/` (environments + release/rollback strategy) + `07-solution/observability/` (`SLO-`, alerts) + the release-readiness checklist.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
