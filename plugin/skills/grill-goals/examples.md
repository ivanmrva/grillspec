# grill-goals — worked example

Illustrative: it shows the shape of the output, not a list to fill. The product is a habit-tracking app that nudges users to log workouts.

> **Agent:** What single metric proves it is working — installs, or loggers who come back? *(I'd make the north star "% of signups logging ≥3 workouts a week in week 4". Installs are a vanity number; the value lands only if the habit sticks.)*
> **User:** Retention, not installs. But I want an earlier signal I can steer on.
> **Agent:** Then a guardrail. If we tune nudges for that, what must not degrade? *(Over-nudging usually cuts notification opt-in and raises uninstalls.)*
> **User:** Guard both. And put the hard stop in writing.

## Output — `north-star.md`
North star: % of new signups logging ≥3 workouts a week in week 4. It proves the habit formed, not just a trial.

Levers: first workout logged within 24 h (activation) · logging in both week 2 and week 4 (retention) · free → paid at week 4 (revenue).

## Output — `success-metrics.md`
| metric | definition | target |
|---|---|---|
| activation | signups logging within 24 h / signups, 7-day window | 60% |
| week-4 retention | week-4 users with ≥3 logs / cohort, 28-day window | 25% |
| guardrail: notification opt-in | users with notifications on / actives | ≥ 70% |
| guardrail: uninstall rate | uninstalls / installed base, monthly | ≤ 8% |

## Output — `kill-criteria.md`
| signal | threshold | deadline | verdict | status |
|---|---|---|---|---|
| week-4 retention | below 15% | week 12 after launch | pivot the nudge model | ratified |
| uninstall rate | above 15% for 2 cohorts in a row | any review | kill | ratified |
| minimum success | week-4 retention ≥ 20% | week 24 after launch | persevere, else stop | ratified |

Review cadence: every 4 weeks.
