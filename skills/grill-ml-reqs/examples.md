# grill-ml-reqs — worked example

Illustrative: it shows the shape of the output, not a list to fill. The capability auto-categorises uploaded receipts in an expense app on the `standard` profile.

> **Agent:** "It works" is not a bar. What are the metric and target for category prediction on a held-out set? *(I'd anchor on macro-F1, not raw accuracy: your categories are imbalanced, and "Meals" dwarfs "Software".)*
> **User:** Macro-F1, and it has to beat the rule-based baseline we ship.
> **Agent:** Below what confidence does the model stop auto-applying and ask the user? A silent wrong category is worse than a question. *(I'd default to 0.80, then offer the top 3 for one tap.)*
> **User:** 0.80 is right. Auto-apply above, suggest below.

## Output — `capabilities.md`
| id | task | I/O | decision it drives | HITL | serves (UC-) | draws-on (DATA-) |
|---|---|---|---|---|---|---|
| ML-002 | classify | in: receipt image + OCR text · out: category + confidence | which ledger category the expense posts to | below threshold the user picks from the top 3; finance approves anything over $2k | UC-022 | DATA-009 |

## Output — `evals.md`
| metric | ML | target | eval-set | pass-bar |
|---|---|---|---|---|
| macro-F1 | ML-002 | ≥ 0.88 and above the rule baseline (0.71) | 4,000 held-out human-labelled receipts, frozen | gates activation |
| top-3 recall | ML-002 | ≥ 0.97 | the same set | gates activation: the suggestion list must contain the truth |

## Output — `quality-bars.md`
| bar | ML | value | fallback |
|---|---|---|---|
| auto-apply error rate | ML-002 | ≤ 8% | — |
| latency and cost per receipt | ML-002 | ≤ 600 ms p95 · ≤ $0.004 | — |
| confidence threshold | ML-002 | 0.80 | below it, show the top 3 plus "Other"; with empty OCR, decline and ask for a clearer photo |

The capability is not trained on the product's own pipeline and does not decide about people, so `data-needs.md` and `responsible-ai.md` were not written. Serving and the eval harness belong to the ML architecture.
