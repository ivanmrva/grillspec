# grill-ml-reqs — worked example

ML requirements for auto-categorizing uploaded receipts in an expense app.
> **Claude:** "It works" isn't a bar — what's the metric and target for category prediction, on a held-out set? *(I'd anchor on macro-F1, not raw accuracy; your categories are imbalanced — "Meals" dwarfs "Software".)*
> **User:** Macro-F1, and it has to beat the rule-based baseline we ship today.
> **Claude:** Below what confidence does the model stop auto-applying and ask the user? Silent wrong categories are worse than asking. *(I'd default 0.80 → present top-3 for one tap.)*
> **User:** 0.80 sounds right; auto-apply above, suggest below.

## Output — `capabilities.md`
| id | task | I/O | decision it drives | HITL |
|---|---|---|---|---|
| ML-002 | classify | in: receipt image + OCR text · out: expense category + confidence | which GL category the expense posts to | below threshold → user picks from top-3; finance approves any >$2k regardless |

## Output — `evals.md`
| metric | target | eval-set | offline + online bar |
|---|---|---|---|
| macro-F1 | ≥ 0.88 and > rule-baseline (0.71) | 4,000 held-out human-labeled receipts, frozen | offline: gate the release · online: canary 5%, auto-apply acceptance (no user edit) ≥ 90% over 7 days |
| top-3 recall | ≥ 0.97 | same held-out set | offline gate (the suggest-list must contain the truth) |

## Output — `data-needs.md`
| source | labelling | volume | refresh |
|---|---|---|---|
| historical user-confirmed receipts | the user's accepted/edited category = label | ~120k seed, +8k/wk | monthly retrain; drift check weekly (PSI on category mix) |

## Output — `quality-bars.md`
- **Error cost:** false category is recoverable (user edits) but erodes trust → cap auto-apply error ≤ 8%; never auto-apply a *tax-deductible* flag.
- **Latency/cost:** ≤ 600 ms p95 per receipt; ≤ $0.004/inference.
- **Fallback (<0.80):** don't auto-apply — show top-3 + "Other"; if OCR empty, decline and request a clearer photo.

## Output — `responsible-ai.md`
| risk | requirement |
|---|---|
| merchant-name bias (non-US vendors mis-categorized) | report macro-F1 sliced by vendor locale; no slice < 0.80 |
| transparency | show "suggested" badge + why (top merchant signal); user can always override |
| misuse | block using category data to infer protected attributes; audit-log overrides |

Recorded: ML-002 anchored on macro-F1 with a baseline to beat; mandatory 0.80 threshold + top-3 fallback; HITL at low-confidence and >$2k; offline gate AND online canary both defined; fairness sliced by locale. Serving architecture and eval-harness code excluded — that's the ML architecture.
