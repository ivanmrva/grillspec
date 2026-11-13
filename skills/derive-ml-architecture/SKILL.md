---
name: derive-ml-architecture
description: >-
  Decide the ML/AI system design from the ML requirements — the model choice and serving path with
  its fallback, and the evaluation gate before promotion; at the regulated profile also the pipeline,
  monitoring, guardrails and model registry. Use when the product has an ML capability.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# derive-ml-architecture

**Load `references/derive-engine.md` first and follow it.** This skill applies that method to the **ML system architecture**: how a model is chosen, served, evaluated and kept safe for each ML capability.

## Depth by profile
The area applies only to a product with an ML capability. How much is written then follows the project's profile:

| Profile | Mode | Written |
|---|---|---|
| `lite` | N/A | nothing here — the model choice, its fallback and the gate before promotion are a row in `arch/solution-strategy.md` |
| `standard` | decision mode | `eval-harness.md`, `serving.md` |
| `regulated` | full mode | those two plus `pipeline.md`, `monitoring.md`, `guardrails.md`, `model-registry.md` |

Decisions live in the spec; the description lives in the artifact that enforces it — here the model gateway and the eval harness in code — and once code exists they are the source of truth for serving and pipeline detail. Decision mode therefore records only which model serves each capability, what happens when it fails, and the bar a model or prompt must clear before promotion; full mode also writes the surrounding design, because at `regulated` it is a deliverable auditors and other teams read.

## Decision record
`serving.md`, per `ML-` capability:
- the model approach, chosen on merit and the constraints: a hosted model/API · a fine-tune · prompt + retrieval · classical ML;
- the model and where it is hosted · sync, async or batch · the latency and cost budget;
- the fallback path: what the user gets when the model times out, fails or is rejected by the gate;
- for a generative or agentic capability, its input and output guardrails (injection, abuse, safety), in one line.

`eval-harness.md`, keyed to the `ML-` capability and its eval ids:
- the offline eval sets and the metric each measures;
- the online or canary evaluation, where the capability has live traffic to evaluate on;
- the gate before promotion: the bar a model or prompt version must pass, and what happens on a regression.

## Rules
- **The data-egress boundary is the organisation's call.** Whether customer or personal data may leave to a third-party or hosted model API is a privacy and residency constraint that can rule the hosted option out entirely. Take it from the requirements, or surface it as a ratify-point before choosing the model approach.
- **Evals gate promotion the way tests gate code.** A model or prompt version ships only after passing its eval bar. At build time a task brief lists under `rules` each `ML-` capability its slice touches, and the eval harness, measured against the stated offline and online bar, is part of that slice's gate.
- **Every model sits behind a contract and a fallback**, so no feature depends on one model with no degraded path.
- **Models and prompts are versioned artifacts**, so a promotion can always be rolled back.

## Output
Written under `solution/ml/`. The rows marked `full` are written only at `regulated`; in decision mode their content is not raised.

| File | Mode | Captures | Format |
|---|---|---|---|
| `serving.md` | decision | the decision record above | typed fields per `ML-` capability |
| `eval-harness.md` | decision | the decision record above | typed fields, keyed to `ML-`/eval ids |
| `pipeline.md` | full | the training, retraining and feedback-data pipeline — or, for an LLM, the prompt, context and retrieval assembly — and the feature store | Mermaid + typed fields |
| `monitoring.md` | full | model-quality and drift signals with their SLOs (the telemetry plumbing belongs to the observability area) | table: signal · SLO |
| `guardrails.md` | full | input and output guardrails · prompt-injection and abuse defence · safety filters · escalation | table: control · mechanism |
| `model-registry.md` | full | models and prompts as versioned, provenance-tracked artifacts · the rollback policy | typed fields |

ADRs → `adr/ADR-MLARCH-NNN.md`
Consumes: the ML requirements and evals · the solution architecture · the data architecture.

## Excludes
training/inference/pipeline code (→ implementation) · the model-behaviour targets (→ the ML requirements) · telemetry plumbing (→ observability)

## Resources
- `references/derive-engine.md`
- Worked example: `examples.md`
