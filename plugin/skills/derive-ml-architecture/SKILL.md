---
name: derive-ml-architecture
description: >-
  Derive the ML/AI system design from the ML requirements — model serving, the evaluation harness, the training/feedback (or prompt/retrieval) pipeline, drift & quality monitoring, guardrails, and model/prompt versioning. Use when an ML/LLM capability's requirements are settled and you need its system architecture derived. Loads the shared derive engine.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-ml-architecture

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **ML system architecture** — serving, evaluation, data/feedback pipelines, monitoring, and guardrails for an ML capability.

## Method
1. choose the model approach per capability (a hosted model/API · fine-tune · prompt + retrieval · classical ML) on merit + the constraints
2. design serving (sync/async/batch · latency/cost · scaling · the fallback path)
3. design the eval harness (the offline eval-sets + the online/canary eval) as the promotion gate
4. design the data/feedback pipeline (training/retraining, or the prompt/context/retrieval assembly) + monitoring & guardrails

## Rules
- **the data-egress boundary is the user's call, not a merit decision** — whether customer/PII data may leave to a **third-party / hosted model API** is a privacy/residency constraint the org holds (it can rule the hosted option out entirely); ratify it, never assume it when picking the model approach
- **evals gate promotion like tests gate code** — no model or prompt ships without passing its eval bar
- **every model behind a contract + a fallback** — never a hard dependency on one model with no degraded path
- **models and prompts are versioned, provenance-tracked artifacts** — rollback is always possible
- for generative/agentic features, input **and** output guardrails (injection · abuse · safety) are mandatory

## Output
Written under `solution/ml/`:

| File | Captures | Format |
|---|---|---|
| `serving.md` | inference architecture per capability: model choice/host · sync/async/batch · latency/cost · scaling · fallback | typed fields |
| `eval-harness.md` | how evals run: offline eval-sets · online/canary eval · the gate before promote (keyed to `ML-`/eval IDs) | typed fields |
| `pipeline.md` | the training/retraining + feedback-data pipeline, or (for an LLM) the prompt/context/retrieval assembly + feature store | Mermaid + typed fields |
| `monitoring.md` | model-quality & drift signals + their SLOs (the telemetry plumbing is the observability area's) | signal · SLO |
| `guardrails.md` | input/output guardrails · prompt-injection/abuse defence · safety filters · escalation | control · mechanism |
| `model-registry.md` | model/prompt versioning · provenance · rollback policy | typed fields |
(+ ADRs → `adr/ADR-MLARCH-NNN.md`)
*(DERIVED & regenerate-only — never hand-edited)*
Consumes: the ML requirements + evals, the solution architecture, and the data architecture.

## Excludes
training/inference/pipeline code (→ implementation) · the model-behaviour *targets* (→ the ML requirements) · telemetry plumbing (→ observability)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
