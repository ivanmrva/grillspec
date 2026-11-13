# deploy-release — worked example

Illustrative. A `standard` project with `trunk` delivery and the promotion path staging → production. The checkout service at version 2.7.0 (tasks T-014 and T-016) is on the default branch.

**Staging.** The push deployed it; the smoke check is green. Nothing more to do for this hop.

**Production — the request to the human.**

> 2.7.0 is ready for production. `preflight` against production is green, staging has run it since the push with no alerts, and the rollback (redeploy 2.6.3) was rehearsed on staging and takes about two minutes. The split-tender feature ships dark behind the flag `checkout.split-tender`. I recommend promoting. Go?

The owner gave the go.

**Rollout.** Deployed through the pipeline as a canary at 10% for 15 minutes. The pipeline's metric gate requires `error_rate < 0.5%` and `p95_latency_ms < 400`; it measured 0.21% and 312 ms and promoted to 100%. Smoke checks green; the checkout availability objective stayed inside its budget for the following hour.

Record — `12-operate/deploy-prod-2.7.0.md`:

| field | value |
|---|---|
| date | 2026-06-02 |
| what · environment · version | checkout service · production · 2.7.0 (T-014, T-016) |
| rollout · gate | canary 10% → 100% · passed (error rate 0.21%, p95 312 ms) |
| go given by | the product owner |
| outcome | live; `checkout.split-tender` still off — enabling it is a separate step |

Had the gate failed, the pipeline would have aborted the canary, and the record would say so with the rollback and the time to recover.
