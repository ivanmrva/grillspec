# derive-ml-architecture — worked example

Illustrative: it shows the shape, not required content.

Upstream: `ML-002` "draft a reply to a customer support email"; target: at least 85% of drafts need no edit, p95 under 4 s; generative and customer-facing.

## Decision mode (`standard`)

`serving.md` — ML-002:
- approach: prompt + retrieval over a hosted model — no labelled set to fine-tune on, and the knowledge base changes weekly
- serving: sync request/response behind an internal `DraftReply` contract; p95 budget 4 s
- fallback: on timeout or a failed output check, return the retrieved knowledge-base snippets and let the agent write manually
- guardrails: retrieved content is quoted, not obeyed; drafts containing another customer's data are blocked

`eval-harness.md` — ML-002:
- offline: 200 labelled tickets → edit-free rate (LLM judge with human spot-check)
- gate: promote only at ≥ 85% and no regression against the current prompt
- online: 5% canary; automatic rollback above an 8% thumbs-down rate

Whether ticket text may be sent to a hosted model is parked as a ratify-point (status: unconfirmed).

## Full mode (`regulated`) adds

A row in `guardrails.md`:

| Direction | Control | Mechanism |
|---|---|---|
| output | PII and safety filter | block drafts with other customers' data; toxicity classifier → escalate to a human |

`model-registry.md` pins prompt, model id and retrieval-index hash as one versioned artifact; rollback repoints the alias.
