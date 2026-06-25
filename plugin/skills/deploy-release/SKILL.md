---
name: deploy-release
description: >-
  Promote a built increment through environments with an explicit rollout/rollback strategy and smoke-verify in the target. Use when a merged increment needs promoting to an environment. Loads the shared exec engine.
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
5. **Run `preflight` in the target environment before serving traffic** (required env vars present · dependencies reachable/authenticating · migrations applied · readiness `/readyz` green) — a failed preflight aborts the promotion; never deploy past a red preflight. Then post-deploy smoke checks + watch the relevant `SLO-`/alerts during rollout; roll back on breach per the defined procedure.
6. Never hand-deploy outside the IaC/CD path.
7. **Extend the setup runbook for this environment** — promoting to a *new* environment (esp. the first production push) fills `12-operate/bootstrap.md` Phases B/C from `infra-ops/environments.md` + `prerequisites.md`: this environment's distinct config keys, the prod-only prerequisites (DNS · certs · scale/residency · prod credentials), the go-live checklist, and day-2 (rotation/scale/new-env). The runbook stays a complete, current step-by-step an operator can follow without guessing — never a value, always where-to-set-it.

## Rules
- The release-readiness checklist is advisory for **pre-prod** environments — ship to dev/stage freely, an unmet item is a known risk. **A PRODUCTION promotion is a human go/no-go**, not auto-proceed: the metric gate decides canary *health*, but the business *go* to prod requires an **explicit human go — unless a once-ratified auto-promote policy exists** (recommended default to ratify: auto-promote dev→stage; require a human go for stage→prod). This is the deploy analogue of `migrate-data`'s owner-ratified cutover. **Never pass on (prod or not):** a missing rollback path · SLOs/alerts not in place · smoke checks failing · an artifact with no verified provenance.
- **The FIRST production promotion passes a Production-Readiness Review (PRR) — a real gate, not a vibe.** A consolidated checklist that mostly *references* existing artifacts and adds the "verified/rehearsed, not just planned" bar: security review passed (no open blocking `SEC-`) · **rollback rehearsed** (not only designed) · **backups proven restorable** (a test-restore was run, not assumed) · DR mechanism exercised to its tier · SLOs + alerts confirmed **receiving data** in prod · `preflight` green · **`check_config_drift.py` clean** (the matrix matches what the code reads) · cost guardrails/anomaly alerts on · the day-2 runbooks exist. An unmet PRR item is **blocking for go-live**, surfaced for the human go/no-go — not silently shipped.
- Canary verdict comes from the metric gate's thresholds, never a subjective read of the dashboards.

## Output
Written under `12-operate/`:

| File / target | Captures | Format |
|---|---|---|
| `deploy-<env>-<version>.md` | deploy record: what · env · version · provenance (level / attestation digest) · reconciled revision · rollout strategy + metric-gate verdict · **change-failed? (Y/N)** · **intervention (hotfix/rollback/forward)** · **recovery-time** · checklist outcome | — |
| `bootstrap.md` (extend) | Phases B/C of the setup runbook for this environment: prod-only prerequisites · this env's distinct config · go-live checklist · day-2 (rotation/scale/new-env) | followed step-by-step; never a value |
| `production-readiness.md` (first prod promotion) | the PRR gate: each item · referenced artifact/evidence · verified? (rehearsed/test-restored, not just planned) · go/no-go verdict | checklist: item · evidence · status |

(the change-failed? / intervention / recovery-time fields feed a change-failure-rate + recovery-time rollup across deploys)

ADRs → `adr/ADR-REL-NNN.md`
(no spec/code changes — operates the running system)
Consumes: the merged increment + `09-solution/infra-ops/` (environments + release/rollback strategy) + `09-solution/observability/` (`SLO-`, alerts) + the release-readiness checklist.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
