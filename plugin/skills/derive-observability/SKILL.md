---
name: derive-observability
description: >-
  Decide the service-level objectives — each SLO with its SLI, objective and whether it pages — and at the regulated profile also the telemetry plan, alerting and runbooks. Use when the NFRs and architecture exist and the running system needs its operating targets.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-observability

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **observability & SLOs**: how the running system is measured, alerted on and operated.

## Depth by profile
How much is written follows the project's profile:

| Profile | Mode | Written |
|---|---|---|
| `lite` | N/A | nothing here — an objective that pages is a row in `arch/solution-strategy.md`, the rest is in the conventions |
| `standard` | decision mode | `slos.md` |
| `regulated` | full mode | `slos.md` plus `telemetry.md`, `alerting.md`, `runbooks.md` |

Decisions live in the spec; the description lives in the artifact that enforces it — here the instrumentation and the alert configuration — and once code exists they are the source of truth for how signals are emitted and alerts are wired. Decision mode therefore records only the objectives: what is measured, to what target, and which breach wakes someone; full mode also writes the telemetry, alerting and runbook design, because at `regulated` it is a deliverable other teams and auditors read.

## Decision record
`slos.md` is written in both modes. Each availability or latency NFR becomes an `SLO-` row with:
- the `NFR-` it operationalises, by id (`maps-to(NFR-)`), on the same row. This keeps an NFR from silently losing its objective and an objective from floating free of a requirement;
- the objective and its window, the SLI that measures it, and the error budget that follows;
- whether a breach pages, opens a ticket, or is only reported.

An objective the upstream NFR left loose is a ratify-point: propose the number and surface it as the engine describes.

## Full mode
At `regulated` the skill also decides and records the items below. In decision mode they are not raised.
- **Telemetry** (`telemetry.md`): the signals that measure each SLO, within a cost, cardinality and sampling budget. Items to decide: wide structured events as the primitive that logs, metrics and traces are views over · emission over OTLP with semantic-convention attribute names through a collector boundary · golden-signal, resource (utilization · saturation · errors) and service (rate · errors · duration) metrics · a security-relevant-events class (authorization failures, privilege changes) · model-quality and drift signals for an ML feature · continuous profiling where a latency or CPU NFR warrants it.
- **Alerting** (`alerting.md`): each alert links an SLO and a runbook, and alerts on a symptom or on budget burn in preference to a cause. Items to decide: multi-window, multi-burn-rate tiers (a fast and a slow window per SLO) · the error-budget policy (for example, freeze releases on exhaustion) · the dashboards.
- **Runbooks** (`runbooks.md`): detect → mitigate → recover for each alert and main failure mode, plus security monitoring, the on-call, escalation and severity model with blameless postmortems, and the DR-drill or game-day plan.

All of this is planned design, not a list of concrete production tasks.

## Output
Written under `solution/observability/`:

| File | Mode | Captures | Format |
|---|---|---|---|
| `slos.md` | decision | the decision record above | table keyed on `SLO-`: maps-to(`NFR-`) · objective · SLI · error budget · on breach |
| `telemetry.md` | full | the telemetry plan | short tables and typed fields |
| `alerting.md` | full | alerts ⇄ SLO and runbook · the error-budget policy · dashboards | table per alert, then typed fields |
| `runbooks.md` | full | per alert or failure mode: detect → mitigate → recover; the on-call model; the drill plan | steps per mode |

ADRs → `adr/ADR-OBS-NNN.md`
Consumes: the availability, latency and security NFRs and the chosen architecture.

## Excludes
telemetry code and agents · infra topology (→ the infrastructure area) · the alerting-tool choice (an ADR if it emerges)

The instrumentation obligation still reaches the build: a task brief lists under `rules` each `SLO-` whose signal its slice must emit, and the slice's tests assert the emission. This area decides the objectives; the tasks ship the signals.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
