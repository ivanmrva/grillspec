# deploy-release — worked example

Promoting a merged increment to production, gated on a real metric gate.

> **Claude:** Artifact `checkout-svc@2.7.0` — provenance SLSA-L3, attestation digest `sha256:9f1c…b4` matches the registry. Provenance OK, it can enter staging.
> Staging reconciled to revision `r-4471` (declarative; the reconciler converged it — no hand-apply). Smoke checks green. Promoting to prod as a **canary** behind flag `checkout.split-tender` (shipped dark).
> Canary 10% for 15 min, metric gate: `error_rate < 0.5%` AND `p95_latency_ms < 400`. Observed `error_rate 0.21%`, `p95 312ms` → **gate PASS, auto-promote** to 100%. (Verdict is the gate's, not my read of the dashboard.)

Recorded — `10-operate/deploy-prod-2.7.0.md`:

| field | value |
|---|---|
| what · env · version | checkout-svc · prod · 2.7.0 |
| provenance | SLSA-L3 · `sha256:9f1c…b4` (verified) |
| reconciled revision | `r-4471` |
| rollout + gate verdict | canary 10→100% · gate PASS (`err 0.21%`, `p95 312ms`) |
| **change-failed?** | **N** |
| intervention | none |
| **recovery-time** | n/a |
| checklist outcome | rollback path ✓ · SLOs/alerts ✓ · smoke ✓ |

(change-failed?/intervention/recovery-time feed the change-failure-rate + recovery-time rollup across deploys. The flag stays off; release is a separate, later toggle.)
