---
name: grill-ml-reqs
description: >-
  Pin the requirements for an AI/ML capability: what the model must do and how well, the eval
  that gates activation, the confidence threshold with its fallback, and where a human reviews.
  Use when the product embeds ML or LLM behaviour.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-ml-reqs

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **ML/AI feature requirements** — the behaviour, evaluation, data, and safety an ML capability must meet, which classical functional + quality requirements can't express.

## Depth by profile
This area exists only for a product with an AI capability. At `regulated` the readiness gate expects the area, so a product without one records `N/A — <why>` in `capabilities.md`.

| Profile | What the interview captures |
|---|---|
| `lite` | not a separate area. |
| `standard` | per capability: the quality bars, the eval that gates activation, and the fallback (`capabilities.md`, `evals.md`, `quality-bars.md`). |
| `regulated`, or where the product has the concern | `data-needs.md`, when the capability is trained or tuned on the product's own data. `responsible-ai.md`, when it decides about people or a regulation imposes a duty. An online (canary) bar beside the offline one. |

## Rules
- Evals are the acceptance criteria for ML. Every model behaviour has a measurable metric, a target and a held-out eval set; "it works" is not a bar. The eval gates activation: a model version that misses the bar is not switched on.
- Every `ML-` capability names the `UC-` it serves by id on its own row, or `N/A — <why>` for an internal capability no use-case surfaces. It names the `DATA-` class it draws on the same way. Ids let a changed use-case or data class be traced to the capability.
- A confidence threshold and a fallback are required. State what happens below the threshold: human hand-off · safe default · decline.
- Name where a person reviews or approves a high-impact decision.
- Every bar, threshold, budget and guardrail is keyed to the `ML-` it bounds, so the task that builds the capability can cite it. A regulatory duty is an `OBL-` in the compliance area, cited here.
- Targets and thresholds are the user's to ratify.

## Output
**IDs:** `ML-` an ML capability (its behaviour, evals and responsible-AI duties).
Written under `requirements/ml/`:

| File | Captures | Format |
|---|---|---|
| `capabilities.md` | per capability: the task (classify · extract · generate · rank · agentic), its inputs and outputs, the decision it drives, the human-in-the-loop point | `ML-NNN` id · task · I/O · decision · HITL · serves(`UC-`) · draws-on(`DATA-`) |
| `evals.md` | the acceptance tests for model behaviour, keyed to their `ML-` | metric · `ML-` ref · target · eval-set · pass-bar (offline; online where set) |
| `quality-bars.md` | acceptable error rates (the cost of a false positive or negative) · per-inference latency and cost budget · the confidence threshold and its fallback | bar · `ML-` ref · value · fallback |
| `data-needs.md` | the training, feedback and label data the capability needs; the class itself lives in the data requirements | data-class(`DATA-`) · source · labelling · volume · refresh/drift cadence |
| `responsible-ai.md` | fairness and bias risks · safety guardrails · transparency and explainability needs · misuse cases | risk · `ML-` ref · requirement · `OBL-` refs |

The `ML-` id leads a row only in `capabilities.md`, where the capability is defined. The other files carry it in a later column, because an id in the leading cell reads as a second definition.

ADRs → `adr/ADR-MLREQ-NNN.md`
Consumes: the use-cases the ML capability serves, and the data classification.

## Excludes
the model/serving architecture, eval harness, and pipelines (→ the ML architecture) · training/inference code · the regulatory *regimes* themselves (→ compliance; here only the requirements they impose)

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
