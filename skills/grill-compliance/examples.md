# grill-compliance — worked example

Pinning the regime for the *AI slot-recommender* that auto-assigns technicians to jobs.

> **Claude:** This model ranks jobs and assigns work to named technicians — that's an employment-context decision, which puts it in EU AI Act high-risk territory, not "limited". Is a human able to override an assignment before it's final? *(I'd require human-oversight + logging here, not just a disclosure banner.)*
> **User:** Right now it auto-commits with no review. We can add an override step.
> **Claude:** Then the obligation is human-in-the-loop plus traceability logging. I'll also fire a fundamental-rights impact assessment, separate from the data-protection one — they trigger independently.
> **User:** Agreed, add both.

Recorded: one high-risk AI component with its obligation checklist; this is obligations, not legal advice — the worker-monitoring angle needs counsel.

## Output
`requirements/compliance/obligations.md`

**OBL-005 — Human oversight of automated technician assignment**
- rule: EU AI Act Art. 14 (high-risk human-oversight) + Art. 12 (logging/traceability)
- forces: a human-reviewable override before an assignment commits; append-only decision log retained for the model's traceability window
- owner: UC override flow (functional) + SEC- audit (security)
- status: applies — system affects workers' allocation (high-risk, employment context)

`requirements/compliance/ai-systems.md`
- component: slot-recommender · tier: **high-risk** · rationale: allocates work to identified employees (Annex III employment use)
- obligations: risk-management · data-governance · logging/traceability · human-oversight · transparency · conformity-assessment
- fundamental-rights-impact-assessment: triggered (separate from the data-protection DPIA)
- flag: worker-monitoring / labour-law angle → needs counsel
