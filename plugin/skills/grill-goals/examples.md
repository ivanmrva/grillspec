# grill-goals — worked example

Defining success for a habit-tracking app that nudges users to log workouts.

> **Claude:** What single metric proves it's working — installs, or weekly active loggers who come back? *(I'd make the north-star "% of signups logging ≥3 workouts/week in week 4" — installs are a vanity number; the value only lands if the habit sticks.)*
> **User:** Retention, not installs. But week 4 is a month out — I want an earlier signal I can actually steer on.
> **Claude:** Then a guardrail: if we optimize nudges for that, what must NOT degrade? *(Over-nudging usually tanks notification opt-in and spikes uninstalls — I'd guard both.)*
> **User:** Guardrails fine. And put the hard stop in writing — last time we limped along on a dead idea for a year before anyone called it.

Recorded:
- `north-star.md` — NSM: "% of new signups logging ≥3 workouts/week in week 4" · why: proves the habit formed, not just trial · causal levers: acquisition=qualified-signup rate · activation=first workout logged within 24h · retention=week-2→week-4 logging continuity (activation def: ≥1 log in first 24h; retention def: logged in both wk2 and wk4) · referral=invites sent per active user · revenue=free→paid at week 4
- `success-metrics.md` — M1 activation: (signups logging within 24h) / (signups) / 7-day window · target 60%. M2 week-4 retention: (wk4 ≥3-log users) / (cohort) / 28-day · target 25%. GUARD-1 notification opt-in must stay ≥70%. GUARD-2 uninstall rate ≤8%/mo
- `kill-criteria.md` — review cadence: every 4 weeks. KC-1 "if week-4 retention not ≥15% by 2026-09-30 → pivot the nudge model." KC-2 "if uninstall rate >15% for 2 consecutive cohorts → kill." Minimum-success criterion: ≥20% week-4 retention with uninstall ≤8% by end of Q4 2026, or stop
