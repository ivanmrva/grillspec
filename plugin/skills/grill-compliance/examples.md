# grill-compliance — worked example

Illustrative: it shows the shape of the output, not a list to fill. The component is an AI slot-recommender that assigns technicians to jobs, for a product operating in the EU.

> **Agent:** This model assigns work to named technicians. That is an employment-context decision, which puts it in EU AI Act high-risk territory. Can a human override an assignment before it is final? *(I'd require human oversight and logging here, not only a disclosure banner.)*
> **User:** It auto-commits with no review. We can add an override step.
> **Agent:** Then the obligations are human oversight and traceability logging. It also triggers a fundamental-rights impact assessment, separate from the data-protection one.
> **User:** Agreed, add both.

## Output — `obligations.md`
| id | rule | forces | owner |
|---|---|---|---|
| OBL-005 | EU AI Act Art. 14, human oversight of a high-risk system | a human can review and override an assignment before it commits | the override use-case |
| OBL-006 | EU AI Act Art. 12, logging and traceability | an append-only log of every assignment decision | SEC-011 (audit rule) |

## Output — `ai-systems.md`
- component: slot-recommender
- tier: high-risk — it allocates work to identified employees (Annex III, employment)
- obligations: OBL-005 (human oversight) · OBL-006 (logging)
- fundamental-rights impact assessment: triggered
- flag: the worker-monitoring and labour-law angle needs counsel

On the `standard` profile nothing required a DPIA document, so `dpia.md` was not written.
