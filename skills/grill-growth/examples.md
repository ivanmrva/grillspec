# grill-growth — worked example

Illustrative: it shows the shape of the output, not a list to fill. A collaborative whiteboard app whose north star is weekly active editors; the user wants activation and its instrumentation, and is not running experiments yet.

> **Agent:** Your compounding loop is the share link: every board invite pulls in an editor who creates their own boards. What is the earliest action that predicts a user sticks?
> **User:** People who invite at least one teammate in week one almost never churn.
> **Agent:** Then I'd set activation as one board shared within 7 days of signup, with 10 minutes from signup to the first shared board as the time-to-value target. Ratify?
> **User:** Yes.

## Output — `growth-model.md`
- funnel: visit → signup → first board → invite → weekly active editor
- activation bar: `board.shared` ≥ 1 within 7 days of signup · time-to-value ≤ 10 min · status: ratified
- retention: weekly cohorts; plateau check at week 8, ≥ 38% of editors retained · stickiness DAU/WAU ≥ 0.45

## Output — `analytics-events.md`
Naming: object-action, from a controlled vocabulary. Cohorts are keyed on signup week.

| id | event | properties | classification | serves | owner |
|---|---|---|---|---|---|
| AEV-001 | `user.signed_up` | plan, referrer | consented analytics | activation (denominator) | Growth PM |
| AEV-002 | `board.shared` | invite_channel, invitee_count | consented analytics | activation bar | Growth PM |
| AEV-003 | `board.edited` | duration_s | consented analytics | retention, stickiness | Growth PM |

No `experiments.md` was written; the team is not experimenting yet.
