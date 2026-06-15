# grill-customer-discovery — worked example

Pinning who a clinical-trial patient-recruitment platform is really for.

> **Claude:** Who's the primary segment — the CRO running the trial, or the individual research-site coordinator chasing enrollment? *(I'd lead with the site coordinator: they feel the enrollment pain daily and can adopt without a procurement cycle; the CRO is the buyer, not the user.)*
> **User:** The site coordinator. They're judged on hitting an enrollment quota and they're drowning in manual chart review.
> **Claude:** For the buying side, who actually signs — is the coordinator also the economic buyer, or is that the site's principal investigator? *(Matters because the PI champions but rarely controls budget.)*
> **User:** PI champions it; the site's research director holds the budget.

Recorded:
- `segments.md` — SEG-1 Research-site coordinator (primary) · JTBD job statement: "when I'm behind on an enrollment quota, I want eligible patients surfaced from our own EHR, so I can hit the deadline without manual chart review" · functional: find eligible patients fast · emotional: relief from quota stress · social: look reliable to the PI · desired outcomes: ≥20 pre-screened referrals/week · traits: 2–5 trials in parallel, EHR-bound
- `icp.md` — firmographics: mid-size academic sites, 5–20 active trials, Epic/Cerner EHR · behaviors: coordinators do manual chart pulls weekly · why-primary: attractiveness (acute quota pain) × reachability (SCRS conferences, site networks) × fit (EHR data already on hand)
- `personas.md` — PERSONA-Coord "Maria" · behaviors: pulls charts manually 6h/wk (evidence: 3 site interviews, 2026-05) · goals: hit quota · context: juggles 4 trials · pains: missed-eligibility, audit fear · interview-grounded. PERSONA-PI "Dr. Okafor" · behaviors: approves tools, no daily use · hypothesis
- `actors.md` — system users: Coordinator (Maria) ✓ ; PI = champion, occasional reviewer ✓ ; Research director = buying role only, NOT a system user
