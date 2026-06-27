---
name: grill-ml-reqs
description: >-
  Pin the requirements for an AI/ML feature — what the model must do and how well, its evaluation criteria (the acceptance tests for model behaviour), the training/feedback data it needs, confidence/fallback bars, human-in-the-loop points, and responsible-AI obligations. Use when the product embeds an ML or LLM capability that classical functional/quality requirements don't capture. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-ml-reqs

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **ML/AI feature requirements** — the behaviour, evaluation, data, and safety an ML capability must meet, which classical functional + quality requirements can't express.

## Rules
- **evals are the acceptance criteria for ML** — every model behaviour has a measurable metric, a target, and a held-out eval set; "it works" is not a bar
- **every `ML-` capability names the `UC-` it serves and the `DATA-` class it draws on, by id** — the serve- and data-relationships the area Consumes are recorded as resolvable ids, never prose (mirrors how an `ENTL-` names its `UC-` capability)
- **a confidence threshold + a fallback is mandatory** — define what happens below it (human handoff · safe default · decline)
- **human-in-the-loop for high-impact decisions** — name where a person reviews or approves
- offline eval (a fixed set) **and** online eval (production/canary) are both required

## Output
**Stable IDs** (bare type prefix, ID = the leading table column / row key): `ML-` an ML capability (its behaviour · evals · responsible-AI duties).
Written under `requirements/ml/`:

| File | Captures | Format |
|---|---|---|
| `capabilities.md` | per ML capability (id `ML-NNN`): the task (classify · extract · generate · rank · agentic) · inputs/outputs · the decision it drives · the human-in-loop point · the `UC-` it serves (`serves(UC-)`) | id · task · I/O · decision · HITL · serves(`UC-`) |
| `evals.md` | the acceptance tests for model behaviour, keyed to their `ML-`: metric · target · eval-set · offline + online pass-bar | metric · target · eval-set · bar |
| `data-needs.md` | training/feedback/label data the capability needs: the `DATA-` class it draws on (`data-class(DATA-)`) · source · labelling · volume · refresh/drift cadence (the data *class* itself lives in the data requirements) | data-class(`DATA-`) · source · labelling · volume · refresh |
| `quality-bars.md` | acceptable error rates (false-pos/neg cost) · per-inference latency & cost budget · low-confidence fallback behaviour | rate · budget · fallback |
| `responsible-ai.md` | fairness/bias risks · safety guardrails · transparency/explainability needs · misuse cases · the regulatory obligations that apply | risk · requirement |
(+ ADRs → `adr/ADR-MLREQ-NNN.md`)
Consumes: the use-cases the ML capability serves, and the data classification.

## Excludes
the model/serving architecture, eval harness, and pipelines (→ the ML architecture) · training/inference code · the regulatory *regimes* themselves (→ compliance; here only the requirements they impose)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
