---
name: derive-observability
description: >-
  Derive the observability design — SLOs/SLIs, telemetry, alerting, dashboards, runbooks — the basis for operating a real system. Use when the NFRs and architecture exist and you need operations designed. Loads the shared derive engine.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-observability

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **Observability & SLOs** — how the running system is measured, alerted on, and operated.

## Method
1. per availability/latency NFR → an `SLO-` + its SLI + error budget
2. the telemetry to measure it — **wide structured events** as the high-cardinality primitive (logs/metrics/traces are views over them), emitted **over OTLP** with **semantic-convention** attribute names through a **collector** pipeline boundary — instrumented per golden signals + the **resource method** (utilization · saturation · errors) + the **service method** (rate · errors · duration)
3. the alert(s) → the runbook on breach → a dashboard; alerting is **multi-window multi-burn-rate** (a fast window + a slow window per SLO)
4. add **continuous profiling** as a signal where latency/CPU NFRs warrant it
5. add the day-2 monitoring — incl. a named **security-relevant-events** telemetry class (authz failures · privilege changes) and **model-quality / drift** signals for ML features — the **on-call / escalation / severity** model + blameless postmortem, and the DR-drill / game-day plan

## Rules
- every availability/latency NFR maps to an `SLO-`, and **each `SLO-` records the `NFR-` it operationalises by id** (`maps-to(NFR-)`) — so an NFR can't silently lose its SLO and an SLO can't float free of a requirement; golden signals + resource method (utilization · saturation · errors) + service method (rate · errors · duration) instrumented
- instrumentation contract: **vendor-neutral telemetry over OTLP**, **semantic-convention** attribute names, a **collector** pipeline boundary; **wide structured events** are the primitive (the three pillars are views over them)
- each alert links an SLO + a runbook; prefer symptom / SLO-burn-rate alerts; burn-rate alerting is **multi-window multi-burn-rate** (fast + slow window tiers)
- **security-relevant events** (authz failures · privilege changes) are a named telemetry class; **model-quality / drift** signals present for ML features
- **continuous profiling** included where a latency/CPU NFR warrants it
- an error-budget policy (freeze releases on exhaustion)
- runbooks exist for the main failure modes; an **on-call / escalation / severity** model + blameless postmortem; day-2 monitoring + DR-drill plan present
- captured as **planned design**, not concrete prod tasks

## Output
Written under `solution/observability/`:

| File | Captures | Format |
|---|---|---|
| `slos.md` | SLOs/SLIs — id SLO-NNN: the `NFR-` it operationalises (`maps-to(NFR-)`) + objective + its SLI + error budget | maps-to(`NFR-`) · objective · SLI · error budget |
| `telemetry.md` | telemetry plan: wide structured events (the primitive) · golden-signal + resource-method + service-method metrics · traces · security-relevant-events class · model-quality/drift signals · continuous profiling — emitted over OTLP w/ semantic-convention names through a collector boundary (within a cost/cardinality/sampling budget) | tight structured fields/tables/bullets |
| `alerting.md` | alerting (alert ⇄ SLO/runbook · symptom · multi-window multi-burn-rate) + error-budget policy + dashboards | tight structured |
| `runbooks.md` | per alert/failure mode: detect → mitigate → recover (+ security monitoring · on-call/escalation/severity + blameless postmortem · DR-drill / game-day plan) | per-mode steps |

ADRs → `adr/ADR-OBS-NNN.md`
*(DERIVED & regenerate-only)*
Consumes: the availability/latency/security NFRs and the chosen architecture.

## Excludes
telemetry code/agents · infra topology (→ the infrastructure area) · alerting-tooling choice (ADR if emergent)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
