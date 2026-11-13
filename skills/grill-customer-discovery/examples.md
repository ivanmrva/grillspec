# grill-customer-discovery — worked example

Illustrative: it shows the shape of the output, not a list to fill. The product is a clinical-trial patient-recruitment platform, sold B2B.

> **Agent:** Who is the primary segment — the CRO running the trial, or the research-site coordinator chasing enrollment? *(I'd lead with the coordinator: they feel the enrollment pain daily and can adopt without a procurement cycle. The CRO buys; it does not use.)*
> **User:** The site coordinator. They are judged on an enrollment quota and they are drowning in manual chart review.
> **Agent:** On the buying side, who signs — the coordinator, or the site's principal investigator? *(The PI champions but rarely controls budget.)*
> **User:** The PI champions it; the site's research director holds the budget.

## Output — `segments.md`
**Research-site coordinator (primary)**
- job statement: when I am behind on an enrollment quota, I want eligible patients surfaced from our own EHR, so I can hit the deadline without manual chart review.
- functional: find eligible patients fast · emotional: relief from quota stress · social: look reliable to the PI
- desired outcome: at least 20 pre-screened referrals a week
- traits: runs 2–5 trials in parallel, works inside the EHR

## Output — `personas.md`
| persona | behaviours (evidence) | goals | pains | grounding |
|---|---|---|---|---|
| Coordinator | pulls charts by hand about 6 h a week (3 site interviews) | hit quota | missed eligibility, audit fear | interview-grounded |
| Principal investigator | approves tools, no daily use | trial completes on time | slow enrollment | hypothesis |

## Output — `actors.md`
| persona | role |
|---|---|
| Coordinator | system user |
| Principal investigator | system user (occasional reviewer) and champion |
| Research director | buying role only |

The user was not choosing between segments, so no `icp.md` was written.
