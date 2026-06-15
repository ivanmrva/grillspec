# derive-ml-architecture — worked example

**Upstream (settled):** `ML-002` "draft a reply to a customer support email"; target: ≥85% drafts need no edit, p95 < 4 s; generative + customer-facing.

Approach chosen on merit: **prompt + retrieval** over a hosted model (no labelled fine-tune set yet; knowledge changes weekly so retrieval beats baking it in).

Serving (`serving.md`):
- model: hosted LLM behind an internal `DraftReply` contract · **sync** request/response · p95 budget 4 s
- fallback: on timeout/eval-fail → return retrieved KB snippets + "agent to write manually" (never a hard dependency on one model)

Eval gate — **evals gate promotion like tests gate code** (`eval-harness.md`):
- offline set: 200 labelled tickets → metric `edit-free rate` (LLM-judge + human spot-check); **promote only if ≥85%** and no regression vs current prompt
- online: 5% canary, auto-rollback if thumbs-down rate > 8%

Guardrails — input **and** output, mandatory for generative (`guardrails.md`):

| Direction | Control | Mechanism |
|---|---|---|
| input | prompt-injection defence | strip/quote retrieved content; instruction-hierarchy system prompt |
| output | PII + safety filter | block drafts containing other customers' data; toxicity classifier → escalate to human |

Versioning (`model-registry.md`): prompt + model-id + retrieval-index hash are one pinned, provenance-tracked artifact `draft-reply@2026.06.1`; rollback = repoint the alias.

Recorded: prompt+retrieval choice, sync serving with a degraded fallback, the ≥85% eval gate + canary for `ML-002`, input/output guardrails, the versioned/rollback-able artifact.
